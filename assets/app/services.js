/*
 * @author: Dimitrios Kanellopoulos
 * @contact: jimmykane9@gmail.com
 */

 "use strict";


/* Notification service
 * It's a shared service and some calls must be handled
 *  */
mainApp.factory('notifications_service', function($rootScope) {

    var notifications_service = {};
    notifications_service.message = '';
    notifications_service.type = '';

    notifications_service.show_notification = function(message, type) {
        notifications_service.message = message;
        notifications_service.type = type;
        notifications_service.broadcastNotification();
    };

    notifications_service.broadcastNotification = function() {
        $rootScope.$broadcast('handleNotification');
    };

    return notifications_service;
});

/* UI service (changes css etc) calls and shares the notifications
 * Only works as a wrapper now. Service of notifications can be used
 * directly instead.
 *  */
mainApp.factory('ui', function(notifications_service) {

    var ui = {};

    /* Notifications now kinda wrapper*/
    ui.show_notification_info = function(msg){
        notifications_service.show_notification(msg, 'info');
    };
    ui.show_notification_warning = function(msg){
        notifications_service.show_notification(msg, 'warning');
    };
    ui.show_notification_error = function(msg){
        notifications_service.show_notification(msg, 'error');
    };

    return ui;
});

/* users_service */
mainApp.factory('users_service', function($http, $q) {

    var users_service = {};
    var user = {};

    var membership_types = {
            'admins': ['admin','owner'],
            'members': ['admin','owner', 'member']
    };

    users_service.get_current_user_async = function() {
        var deffered = $q.defer();
        $http.post('/AJAX/person/get/current', {

        })
        .success(function(response, status, headers, config) {
            if (response.status.code !== 200){
                deffered.resolve(response.status);
                return;
            }
            angular.extend(user, response.data);
            //console.log(user)
            deffered.resolve(response.status);
        })
        .error(function(response, status, headers, config) {
            deffered.reject(response.status);
            logging.error(response, status, headers, config);
        });
        return deffered.promise;
    };

    users_service.is_owner_or_admin = function(user, jukebox){
        //console.log("Security Check");
        if (!user.id || !user.memberships)
            return false;
        for (var i=0; i < user.memberships.length; i++ ){
            if (user.memberships[i].jukebox_id === jukebox.id
            && membership_types.admins.indexOf(user.memberships[i].type) !== -1){
                user.is_admin = true;
                return true;
            }
        }
        return false;
    };

    users_service.is_member = function(user, jukebox){
        //console.log("Security check", user);
        if (!user.id || !user.memberships)
            return false;
        for (var i=0; i < user.memberships.length; i++ ){
            if (user.memberships[i].jukebox_id === jukebox.id
            && membership_types.members.indexOf(user.memberships[i].type) !== -1){
                user.is_member = true;
                return true;
            }
        }
        return false;
    };

    users_service.user = function() {
        return user;
    };

    return users_service;
});