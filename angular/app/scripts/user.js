'use strict';

angular.module('app')

  .factory('USER', function($window, $q, $http, SETTINGS, $rootScope, jwtHelper) {
    var USER = {};
    USER.get = function() {
      if ($window.sessionStorage.userToken) {
        var payload = jwtHelper.decodeToken($window.sessionStorage.userToken);
        return {
          'username': payload.username,
          'isCandidate': payload.isCandidate
        };
      } else {
        return false;
      }
    };
    USER.login = function(credentials) {
      return $q(function(resolve, reject) {
        $http
          .post(SETTINGS.backend+'/api-token-auth/', credentials)
          .success(function(data) {
            $window.sessionStorage.userToken = data.token;
            resolve(USER.get());
          })
          .error(function() {
            delete $window.sessionStorage.userToken;
            reject();
          })
        ;
      }).finally(function() {
        $rootScope.$broadcast('USER.change');
      });
    };
    USER.logout = function() {
      delete $window.sessionStorage.userToken;
      $rootScope.$broadcast('USER.change');
    };
    return USER;
  })

  .factory('authInterceptor', function($rootScope, $q, $window, SETTINGS, MESSAGES) {
    return {
      request: function (config) {
        config.headers = config.headers || {};
        if ($window.sessionStorage.userToken) {
          config.headers.Authorization = 'JWT ' + $window.sessionStorage.userToken;
        }
        return config;
      },
      responseError: function (response) {
        if (response.status === 401) {
          MESSAGES.add('global', 'danger', 'Your login token is expired, <a onClick="window.location.reload()">Click here to re-login</a>.');
        } else if (response.status == 0) {
          MESSAGES.add('global', 'danger', 'Failed to contact the backend server at <a href="'+SETTINGS.backend+'">'+SETTINGS.backend+'</a>');
        }
        return response || $q.when(response);
      }
    };
  })

  .config(['$httpProvider', function($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
  }])

  .controller('LoginController', function($scope, USER, MESSAGES, $window, $location) {
    $scope.error = '';
    $scope.credentials = {
      'username': '',
      'password': ''
    };
    $scope.login = function(credentials) {
      USER.login(credentials).then(function() {
        MESSAGES.addAfterLocation('/', 'global', 'info', 'Successfully logged in.');
      }).catch(function() {
        MESSAGES.add('global', 'danger', 'Invalid username or password.');
      });
    };
    $scope.cancel = function() {
      $location.path('/');
    }
  })

;
