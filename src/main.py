import json

from src.config import Config
from src.github.graphql_call import GraphQLCall

if __name__ == '__main__':
    conf = Config()
    query = GraphQLCall('''{{
                      organization(login: {org_name}) {{
                        repositories(first: 100, after: {after}) {{
                          edges {{
                            node {{
                              url,
                              vulnerabilityAlerts(first: 100) {{
                                edges {{
                                  node {{
                                    securityVulnerability {{
                                      package {{
                                        ecosystem
                                        name
                                      }}
                                      firstPatchedVersion {{
                                        identifier
                                      }}
                                      vulnerableVersionRange
                                      severity
                                    }}
                                  }}
                                }}
                                pageInfo {{
                                  hasNextPage
                                  endCursor
                                }}
                              }}
                            }}
                          }}
                          pageInfo {{
                            hasNextPage
                            endCursor
                          }}
                        }}
                      }}
                    }}''')
    out = query.pages(conf.github.access_token, cursor_var_name='after', org_name=conf.github.org_name)
    print([json.dumps(out, indent=2))