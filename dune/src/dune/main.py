from dotenv import load_dotenv
from mcp.server import FastMCP
from dune_client.client import DuneClient
from dune_client.query import QueryBase, QueryParameter

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

@mcp.tool()
def list_chains_and_tables() -> dict[str, list[str]]:
    """
    List the available tables for selected chains, e.g. bitcoin.blocks, ethereum.transactions, etc.
    """
    return CHAINS_AND_TABLES

@mcp.tool()
def get_schema_for_table(chain: str, table_name: str) -> str:
    """
    List the schema (column names and datatypes) for table `chain.table_name`, e.g. bitcoin.blocks,
    ethereum.transactions, etc. Always use this tool before writing an SQL query.
    """
    # https://dune.com/queries/3424601
    query = QueryBase(
        name="Schema query",
        query_id=3424601,
        params=[
            QueryParameter.text_type(name="table_schema", value=chain),
            QueryParameter.text_type(name="table_name", value=table_name),
        ])
    try:
        dune = DuneClient.from_env()
        results = dune.run_query(query)
        return results
    except Exception as e:
        print(f'Error in get_schema_for_table: {str(e)}', file=sys.stderr)
        raise

# Note: This tool requires a paid Dune API key
@mcp.tool()
def create_dune_query(query_name: str, query_sql: str, params: list[str]) -> str:
    """
    Tool to create a Dune Analytics query, returns the query id. The query must
    be run before the result is queried. Use this AT MOST ONCE to answer a user's
    question. Use `update_dune_query` to fix bad queries.
    """
    try:
        dune = DuneClient.from_env()
        query_id = dune.create_query(query_name, query_sql, params)
        return query_id
    except Exception as e:
        print(f'Error in create_dune_query: {str(e)}', file=sys.stderr)
        raise


@mcp.tool()
def update_dune_query(query_id: int, query_sql: str) -> str:
    """
    Tool to update an existing Dune Analytics query.
    Use this to fix the syntax of existing queries with an SQL syntax error.
    """
    try:
        dune = DuneClient.from_env()
        query_id = dune.update_query(query_id, query_sql)
        return query_id
    except Exception as e:
        print(f'Error in update_dune_query: {str(e)}', file=sys.stderr)
        raise


@mcp.tool()
def run_dune_query(query_id: int) -> str:
    """
    Tool to run a Dune Analytics query, returns the result. This returns up-to-date results.
    """
    dune = DuneClient.from_env()
    query = QueryBase(query_id=query_id)
    query_result = dune.run_query(query)
    print(f"run_dune_query result: {query_result}", file=sys.stderr)
    return query_result


@mcp.tool()
def get_dune_query_last_result(query_id: int) -> str:
    """
    Fast MCP tool to get the result of a Dune Analytics query by query id. This returns the result
    from the last time the query was run, which may be out of date.
    """
    # TODO: SDK doesn't return the detailed error message
    # try:
    #     dune = DuneClient.from_env()
    #     query_result = dune.get_latest_result(query_id)
    #     return query_result
    # except Exception as e:
    #     error_message = str(e)
    #     print(f'Error in get_dune_query_result: {error_message}', file=sys.stderr)
    #     # Return the error message instead of raising the exception
    #     return {"error": error_message}

    # Querying with requests returns detailed error message
    import requests
    import json

    def get_dune_results_with_requests(query_id, api_key):
        url = f"https://api.dune.com/api/v1/query/{query_id}/results"
        headers = {
            "X-DUNE-API-KEY": api_key
        }

        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

    api_key = os.getenv('DUNE_API_KEY')
    result = get_dune_results_with_requests(query_id, api_key)
    return json.dumps(result, indent=2)

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


# TODO: For some reason this is never used by Claude desktop
@mcp.prompt()
def fix_sql(original_sql: str) -> str:
    """
    Fix the syntax of an SQL query. Get this prompt when you need to fix a query.
    """
    return "Use the following interval syntax: \"interval '2' day\", \"interval '3' hour\", \"interval '1' month\""

def main():
    print('Running MCP server...', file=sys.stderr)
    mcp.run()

# Run the server
if __name__ == "__main__":
    main()

EVM_STANDARD_TABLES: list[str] = ["blocks","creation_traces","logs","logs_decoded","traces","traces_decoded","transactions"]

CHAINS_AND_TABLES: dict[str, list[str]] = {
    "base": EVM_STANDARD_TABLES,
    "bitcoin": ["blocks", "inputs", "outputs", "transactions"],
    "bnb": EVM_STANDARD_TABLES,
    "ethereum": EVM_STANDARD_TABLES,
    "optimism": EVM_STANDARD_TABLES,
    "polkadot": ["balances", "blocks", "calls", "events", "extrinsics", "stakings", "traces", "transfers"],
    "polygon": EVM_STANDARD_TABLES,
    "sepolia": EVM_STANDARD_TABLES,
    "solana": ["account_activity", "blocks", "discriminators", "instruction_calls", "rewards", "transactions", "vote_transactions"],
    "worldchain": EVM_STANDARD_TABLES,
    "zksync": EVM_STANDARD_TABLES
}
