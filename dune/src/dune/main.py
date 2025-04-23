from dotenv import load_dotenv
from mcp.server import FastMCP
from dune_client.client import DuneClient
# from dune_client.types import QueryParameter
import sys, os
import requests

load_dotenv()
required_env_vars = ['DUNE_API_KEY']  # Add any other required env vars
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f'Error: Missing required environment variables: {missing_vars}', file=sys.stderr)
    sys.exit(1)


# Initialize MCP server
mcp = FastMCP(
    name="Dune Analytics MCP Server",
    description="Dune Analytics tools",
)

# Note: This tool requires a paid Dune API key
@mcp.tool()
def create_dune_query(query_name: str, query_sql: str, params: list[str]) -> str:
    """
    Fast MCP tool to create a Dune Analytics query, returns the query id.
    """
    try:
        dune = DuneClient.from_env()
        query_id = dune.create_query(query_name, query_sql, params)
        return query_id
    except Exception as e:
        print(f'Error in create_dune_query: {str(e)}', file=sys.stderr)
        raise


@mcp.tool()
def get_dune_query_result(query_id: int) -> str:
    """
    Fast MCP tool to get the result of a Dune Analytics query by query id.
    """
    try:
        dune = DuneClient.from_env()
        query_result = dune.get_latest_result(query_id)
        return query_result
    except Exception as e:
        print(f'Error in get_dune_query_result: {str(e)}', file=sys.stderr)
        raise


# https://docs.dune.com/echo/evm/balances
@mcp.tool()
def get_token_balances(address: str) -> str:
    """
    Returns EVM token balances for an address for any token that the address has interacted with
    """

    # TODO: parameter exclude_spam_tokens
    url = f"https://api.dune.com/api/echo/v1/balances/evm/{address}?exclude_spam_tokens"

    headers = {"X-Dune-Api-Key": os.getenv('DUNE_API_KEY')}

    response = requests.request("GET", url, headers=headers)
    return response.text


# https://docs.dune.com/echo/evm/transactions
@mcp.tool()
def get_transaction_data(address: str) -> str:
    """
    Query Dune Analytics for transactions for a given address across several EVM chains. Returns ABI-decoded transaction data.
    """
    url = f"https://api.dune.com/api/echo/v1/transactions/evm/{address}?decode=true"

    headers = {"X-Dune-Api-Key": os.getenv('DUNE_API_KEY')}

    response = requests.request("GET", url, headers=headers)
    return response.text


# https://docs.dune.com/echo/evm/tokens
@mcp.tool()
def get_token_prices(token_address: str) -> str:
    """
    Query Dune Analytics for price data of an ERC-20 token. Returns Token metadata (symbol, name, decimals),
    Current USD pricing information, Supply information, Logo URLs when available
    """

    url = f"https://api.dune.com/api/echo/beta/tokens/evm/{token_address}"

    headers = {"X-Dune-Api-Key": os.getenv('DUNE_API_KEY')}

    response = requests.request("GET", url, headers=headers)
    return response.text


# https://docs.dune.com/echo/evm/tokens
@mcp.tool()
def get_token_contract_info(token_address: str, chain_id: str) -> str:
    """
    Given an ERC-20 token address and a chain id, the API returns:
    Token metadata (symbol, name, decimals)
    Current USD pricing information
    Supply information
    Logo URLs when available

    If the token address is 'native' then returns info on the chain's native token.

    If the chain_id is 'all', returns info for all chains the contract is deployed on.
    """

    url = f"https://api.dune.com/api/echo/beta/tokens/evm/{token_address}?chain_ids={chain_id}"

    headers = {"X-Dune-Api-Key": os.getenv('DUNE_API_KEY')}

    response = requests.request("GET", url, headers=headers)
    return response.text


def main():
    print('Running MCP server...', file=sys.stderr)
    mcp.run()

# Run the server
if __name__ == "__main__":
    main()
