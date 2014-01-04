"use strict"


# Declare app level module which depends on filters, and services
angular.module("app", [
  "utils"
])


### Init ###

angular.element(document).ready ->
  angular.bootstrap(document, ["app"])
