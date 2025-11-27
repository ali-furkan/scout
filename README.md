# Scoutview

Scoutview is a ML based football analytics platform that analyzes historical match data to extract team skill genres and predicts future match outcomes using clustering, ensemble models, and probabilistic goal modeling.

The system is designed as an end-to-end pipeline: data collection, feature engineering, modeling, prediction, and visual presentation through a web interface.

## Development Environment

[devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) used to set up the development environment. Once the environment is ready to use, you can run the project with:
```task <apps>:run```

## Running the Project

To start all services using Docker:

```bash
docker-compose up -d
```

Once running and train a model*, you can access the UI to view predictions, visualizations, and simulation results.

