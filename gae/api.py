import endpoints

import main_api

api_services = list()
api_services.extend(main_api.api_services)
app = endpoints.api_server(api_services)
