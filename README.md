# OllamaProxy

A lightweight security proxy for [Ollama](https://ollama.ai/), providing Bearer Token authentication and basic access control.

## Features

- 🔒 Bearer Token authentication
- 👑 Two-tier access control with regular and master tokens
- 🎯 Configurable endpoint access permissions
- 🐳 Docker-ready with docker-compose setup
- 🚀 Simple Flask app running on Gunicorn
- 🔧 Easy configuration through environment variables

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/ingo.sehnbruch/OllamaProxy.git
   cd OllamaProxy
   ```

2. Copy the example environment file and configure your settings:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` to set your authentication tokens and other configurations.
   ```bash
   nano .env
   ```

3. Start the services using Docker Compose:
   ```bash
   docker-compose up -d
   ```

The proxy will be available at `http://localhost:<LISTEN_PORT>` (default: 80).

## Configuration

### Environment Variables

- `AUTH_TOKEN`: Required token for basic access
- `MASTER_TOKEN`: Optional token for administrative access
- `LISTEN_PORT`: Port for the proxy (default: 80)
- `FORWARD_PORT`: Ollama server port (default: 11434)
- `OLLAMA_HOST`: Ollama image/hostname (default: localhost)
- `PROTOCOL`: Connection protocol (default: http)
- `DEBUG`: Enable debug logging (default: false)

### Endpoint Access Control

Configure which endpoints require master token access:

Default allowing regular token:
- `GENERATE_REQUIRES_MASTER` - generate
- `CHAT_REQUIRES_MASTER` - chat
- `LIST_REQUIRES_MASTER` - list available models
- `SHOW_REQUIRES_MASTER` - show model info

Default requiring master token:
- `CREATE_REQUIRES_MASTER` - create a new model
- `COPY_REQUIRES_MASTER` - copy an existing model
- `DELETE_REQUIRES_MASTER` - delete a model
- `PULL_REQUIRES_MASTER` - pull a model
- `PUSH_REQUIRES_MASTER` - push a model
- `EMBEDDINGS_REQUIRES_MASTER`- embeddings
- `PS_REQUIRES_MASTER` - list active models



## Usage

Send requests to the proxy with the Bearer token in the Authorization header:

```bash
# Regular access
curl -X POST http://localhost:80/api/chat \
  -H "Authorization: Bearer your-auth-token" \
  -d '{"model": "llama3.2:1b", "messages": [{"role": "user", "content": "Hello!"}]}'

# Master access (for protected endpoints)
curl -X POST http://localhost:80/api/pull \
  -H "Authorization: Bearer your-master-token" \
  -d '{"name": "llama3.2:3b"}'
```

(change ports and tokens as set in .env)

## Security Notes

- Always use strong, unique tokens for authentication
- Regularly update dependencies and the Ollama image

## License

This project is released under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.