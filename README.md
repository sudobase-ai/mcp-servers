# sudobase-ai MCP Servers

## Adding servers

Open a PR to this repo, adding the appropriate yaml file.  See below for file details.  The file must be placed in a new directory of this repo with an appropriate name.

## MCP Servers

An MCP server is defined by a directory with a `sudomcp.yml` file, describing the MCP server and how to launch it.
In some cases, the directory may also contain code, but in general commands such as `npx` and `uvx` are used to launch servers without needing to download code.

Available attributes include:

| attribute | description |
|---|---|
| `name` | The unique short name for the server (no spaces). |
| `title` | The full name of the server. |
| `description` | Description of the MCP server's functionality. |
| `local` | (Optional) boolean determining whether the server should launch on the client machine, or be hosted.  Defaults to `false` (hosted) |
| `logo_url` | Url of an image for the server.  Can refer to this repository. |
| `config_schema` | If configuration options are required for the server (such as API keys), these options are described here.  See below for examples. |
| `stdio_server_parameters` | The `command`, `args` (command line arguments) and `env` (environment variables) required to launch the server. |

For examples, see:
- [Dune](dune/sudomcp.yml) for a hosted server with a single API key.
- [Slack](slack/sudomcp.yml) for a hosted server with multiple config options.
- [Google drive](google-drive/sudomcp.yml) for a local server with configuration options.

### Name Collisions
Server `name`s must be unique across all servers. Names may contain slashes, as in `my_github_handle/my_server`. Server `title`s do not need to be unique.

## Bundles

Bundles are a set of MCP servers that can be installed together to provide a logical unit of functionality.  For example, the `blockchain` bundle provides a suite of servers exposing functionality related to querying blockchains.

A bundle is defined by a single yaml file in the [bundles](./bundles) directory.  Bundle attributes include:

| attribute | description |
|---|---|
| `name` | The unique short name for the bundle (no spaces). |
| `title` | The full name of the bundle |
| `description` | Description of the bundle |
| `logo_url` | Url of an image for the bundle |
| `servers` | A list of server names that make up the bundle |

For examples, see:
- [Blockchain](./bundles/blockchain.yml) for a bundle of blockchain-related servers
- [Travel](./bundles/travel.yml) for travel related servers
- [Research](./bundles/research.yml) for assisting with research queries

