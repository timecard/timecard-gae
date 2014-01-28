import endpoints

api = endpoints.api(name="timecard", version="dev",
                    description = "timecard API",
                    allowed_client_ids = [
                      endpoints.API_EXPLORER_CLIENT_ID,
                      "636938638718.apps.googleusercontent.com",
                    ],
                   )

api_services = [api]
