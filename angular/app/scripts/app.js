'use strict';

angular
  .module('app', [
    'ngAnimate',
    'ngAria',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'angular-jwt'
  ])

  .controller('AppController', function($scope, USER, MESSAGES, $rootScope) {
    $scope.user = USER.get();
    $scope.MESSAGES = MESSAGES;
    $scope.logout = function() {
      USER.logout();
      MESSAGES.add('global', 'info', 'Successfully logged out.');
    };
    $rootScope.$on('USER.change', function(){
      $scope.user = USER.get();
    })
  })

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/home.html',
        controller: 'HomeController'
      })
      .when('/login', {
        templateUrl: 'views/login.html',
        controller: 'LoginController'
      })
      .otherwise({
        redirectTo: '/'
      });
  })

  .factory('MESSAGES', function($rootScope, $sce, $location) {
    var clearOnRouteChange = true;
    var scopes = {};
    // clear all messages when route changes
    $rootScope.$on("$routeChangeSuccess", function() {
      if (clearOnRouteChange) {
        scopes = {};
      } else {
        clearOnRouteChange = true;
      }
    });
    return {
      add: function(scope, type, msg, isHtml) {
        if (!scopes[scope]) scopes[scope] = [];
        var obj = {'type': type, 'msg': msg};
        if (isHtml) obj.isHtml = true;
        var exists = false;
        angular.forEach(scopes[scope], function(aobj) {
          if (aobj.type == obj.type && aobj.msg == obj.msg) {
            exists = true;
          }
        });
        if (!exists) {
          if (obj.isHtml) {
            obj.msg = $sce.trustAsHtml(obj.msg);
          }
          scopes[scope].push(obj);
        }
      },
      get: function(scope) {
        if (!scopes[scope]) {
          scopes[scope] = [];
        }
        return scopes[scope];
      },
      addAfterLocation: function(path, scope, type, msg, isHtml) {
        this.setClearOnRouteChange(false);
        this.add(scope, type, msg, isHtml);
        $location.path(path);
      },
      setClearOnRouteChange: function(what) {
        clearOnRouteChange = ((typeof(what) == 'undefined') ? true : what);
      },
      clear: function(scope) {
        scopes[scope] = [];
      }
    };
  })

;
