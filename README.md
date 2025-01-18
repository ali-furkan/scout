# Scoutview

## Development Environment Setup

[devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) is used to setup the development environment. The development environment is setup using the following steps:
- Install [Docker](https://docs.docker.com/get-docker/)
- Install [Visual Studio Code](https://code.visualstudio.com/)
- Install [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension in Visual Studio Code
- Clone the repository and open it in Visual Studio Code
- Click on the green icon in the bottom left corner of Visual Studio Code and select `Reopen in Container`
- The development environment is setup and ready to use. Now you can run the project as `task <apps>:run`

## Running the Project

```bash
docker-compose up -d
```

