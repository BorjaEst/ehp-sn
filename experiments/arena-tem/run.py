from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mlflow
from arena_tem.configuration import ArenaTEMRunConfiguration
from ehp_research.evaluation.arena import evaluate_tem
from ehp_research.training.tem import train_tem
from ehp_sn import ArtifactRef, ArtifactRepository, ExperimentMetadata, load_configuration

EXPERIMENT_ROOT = Path(__file__).resolve().parent
EXPERIMENT_TOML = EXPERIMENT_ROOT / "experiment.toml"


@dataclass(frozen=True)
class ExperimentRunResult:
    run_id: str
    experiment_name: str
    training_corpus_ref: ArtifactRef
    model_ref: ArtifactRef
    evaluation_corpus_ref: ArtifactRef
    evaluation_ref: ArtifactRef


def run(
    configuration_path: Path,
    *,
    repository: ArtifactRepository | None = None,
) -> ExperimentRunResult:
    if repository is None:
        repository = ArtifactRepository.from_environment()

    experiment = load_configuration(EXPERIMENT_TOML, schema=ExperimentMetadata)
    configuration = load_configuration(configuration_path, schema=ArenaTEMRunConfiguration)

    training_corpus = repository.load(configuration.training_corpus)
    evaluation_corpus = repository.load(configuration.evaluation_corpus)

    mlflow.set_experiment(experiment.name)
    with mlflow.start_run(run_name=configuration.run_name) as run:
        mlflow.log_dict(configuration.model_dump(), "configuration.json")

        training_result = train_tem(
            model_settings=configuration.model_settings,
            adapter=configuration.adapter,
            controller=configuration.controller,
            objective=configuration.objective,
            training_settings=configuration.training_settings,
            corpus=training_corpus,
            partition=configuration.partitions["training"],
        )
        model_ref = repository.publish(training_result.model_artifact)

        evaluation_result = evaluate_tem(
            model_ref=model_ref,
            repository=repository,
            evaluation_settings=configuration.evaluation_settings,
            corpus=evaluation_corpus,
            partition=configuration.partitions["evaluation"],
        )
        evaluation_ref = repository.publish(evaluation_result.evaluation_artifact)
        mlflow.log_metrics(evaluation_result.metrics)

        return ExperimentRunResult(
            run_id=run.info.run_id,
            experiment_name=experiment.name,
            training_corpus_ref=configuration.training_corpus,
            model_ref=model_ref,
            evaluation_corpus_ref=configuration.evaluation_corpus,
            evaluation_ref=evaluation_ref,
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("usage: run.py <configuration.toml>")

    result = run(Path(sys.argv[1]))

    print(f"run_id={result.run_id}")
    print(f"model_ref={result.model_ref}")
    print(f"evaluation_ref={result.evaluation_ref}")
