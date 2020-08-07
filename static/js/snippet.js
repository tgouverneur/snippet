
document.head = document.head || document.getElementsByTagName('head')[0];

function changeFavicon(src) {
    var link = document.createElement('link'),
    oldLink = document.getElementById('dynamic-favicon');
    link.id = 'dynamic-favicon';
    link.rel = 'shortcut icon';
    link.href = src;
    if (oldLink) {
        document.head.removeChild(oldLink);
    }
    document.head.appendChild(link);
}

/*
 * Check if snippet needs contract signing before being shown
 * adapt page design accordingly
 */
function loadSnippetPage() {
    res = window.location.hash.substring(1).split('-');
    if (res.length < 2) {
        res = window.location.hash.substring(1).split('#');
        if (res.length < 2) {
            $('#msgError').text('Key and/or UID not provided');
            $('#msgError').show();
            $('#snippetButton').hide();
            return;
        }
    }
    $('#snippetButton').show();
    return;
}

/*
 * Submit snippet to API for creation.
 */
function snippetSubmit() {
    $('#snippetBox').hide();
    $('#snippetLink').attr('href', '');
    $('#snippetLink').text('');
    opts = {};
    opts['content'] = $('#content').val();
    opts['isRaw'] = 0;
    opts['isFile'] = 0;
    opts['isConfirm'] = 0;
    opts['email'] = '';
    opts['name'] = '';
    opts['reference'] = '';
    if ($('#snippet_reference').val() != '') {
        opts['reference'] = $('#snippet_reference').val();
    }
    if ($('#snippet_email').val() != '') {
        opts['email'] = $('#snippet_email').val();
        if (!isEmail(opts['email'])) {
            $('#msgError').text('Email provided is not valid!');
            $('#msgError').show();
            return;
        }
    }
    if ($('#fileMode').prop('checked')) {
        opts['isFile'] = 1;
    }
    if ($('#snippet_isRaw').prop('checked')) {
        opts['isRaw'] = 1;
    }
    if ($('#snippet_confirm').prop('checked')) {
        opts['isConfirm'] = 1;
    }
    if (opts['isConfirm'] == 1 && (opts['email'] == '' || opts['reference'] == '')) {
        $('#msgError').text('Email and Reference must be filled if you want read confirmation.');
        $('#msgError').show();
        return;
    }
    url = null;
    if (opts['isFile']) {
        var file = $('#inputFile')[0].files;
        if (file.length != 1) {
            $('#msgError').text('You should select a file while in File Mode!');
            $('#msgError').show();
            return;
        }
        opts['name'] = file.name;
        var reader = new FileReader();
        reader.onerror = function(error) {
            $('#msgError').text(data.error);
            $('#msgError').show();
            return;
        };
        reader.onload = function() {
            opts['content'] = reader.result;
            $.ajax({
                type: 'POST',
                url: '/api/snippet',
                data: JSON.stringify(opts),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){
                    if (data.rc < 0) {
                        $('#msgError').text(data.error);
                        $('#msgError').show();
                    } else {
                        link = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '') + '/view.html#' + data['id'] + '-' + data['key'];
                        $('#msgError').hide();
                        $('#snippetLink').attr('href', link);
                        $('#snippetLink').text(link);
                        $('#snippetBox').show();
                        $('#createForm').hide();
                    }
                },
                statusCode: {
                    500: function() {
                        $('#msgError').text('The server encountered a fatal error, please contact administrator');
                        $('#msgError').show();
                    }
                },
                failure: function(errMsg) {
                    $('#msgError').text(errMsg);
                    $('#msgError').show();
                }
            });
        };
        reader.readAsDataURL(file[0]);
        return;
    } else {
        if (opts['content'] == '') {
            $('#msgError').text('You should fill the snippet!');
            $('#msgError').show();
            return;
        }
    }
    $.ajax({
        type: 'POST',
        url: '/api/snippet',
        data: JSON.stringify(opts),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            if (data.rc < 0) {
                $('#msgError').text(data.error);
                $('#msgError').show();
            } else {
                link = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '') + '/view.html#' + data['id'] + '-' + data['key'];
                $('#msgError').hide();
                $('#snippetLink').attr('href', link);
                $('#snippetLink').text(link);
                $('#snippetBox').show();
                $('#createForm').hide();
            }
        },
        statusCode: {
            500: function() {
                $('#msgError').text('The server encountered a fatal error, please contact administrator');
                $('#msgError').show();
            }
        },
        failure: function(errMsg) {
            $('#msgError').text(errMsg);
            $('#msgError').show();
        }
    });
}

/*
 * Actually get snippet from API and show it eventually.
 */
function getSnippet() {
    res = window.location.hash.substring(1).split('-');
    if (res.length < 2) {
        res = window.location.hash.substring(1).split('#');
        if (res.length < 2) {
            $('#msgError').text('Key and/or UID not provided');
            $('#msgError').show();
            $('#snippetButton').hide();
            return;
        }
    }
    uid = res[0]
    key = res[1]
    $.ajax({
        type: 'GET',
        url: '/api/snippet/' + uid + '/' + key,
        success: function(data){
            if (data.rc < 0) {
                $('#msgError').text(data.error);
                $('#msgError').show();
                $('#snippetButton').hide();
            } else {
                if (data['isFile']) {
                    var a = document.createElement('a');
                    if (window.URL && window.Blob && ('download' in a) && window.atob) {
                        // Do it the HTML5 compliant way
                        var blob = base64ToBlob(data['content'], 'application/octet-stream');
                        var url = window.URL.createObjectURL(blob);
                        a.href = url;
                        a.download = result.download.filename;
                        a.click();
                        window.URL.revokeObjectURL(url);
                    } else {
                        $('#msgError').text('Your browser is too old.. and unfortunately the data is lost.');
                        $('#msgError').show();
                        $('#snippetButton').hide();
                        return;
                    }
                } else {
                    if (data['isRaw']) {
                        content = '<pre>' + data['content'] + '</pre>';
                    } else {
                        content = data['content'];
                    }
                    $('#snippet').html(content);
                    $('#snippet').show();
                    $('#snippetButton').hide();
                }
            }
        },
        failure: function(errMsg) {
            $('#msgError').text(errMsg);
            $('#msgError').show();
            $('#header').hide();
        }
    });
}

function toggleFileMode() {
    if ($('#fileMode').prop('checked')) {
        $('#contentInput').hide();
        $('#fileInput').show();
    } else {
        $('#fileInput').hide();
        $('#contentInput').show();
    }
}

function toggleAdvancedMode() {
    if ($('#advancedMode').prop('checked')) {
        $('#advancedInput').show();
    } else {
        $('#advancedInput').hide();
    }
}

/**
 * Validate email address for simple validity
 */
function isEmail(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

/**
 * base64ToBlob
 */
function base64ToBlob(base64, mimetype, slicesize) {
    if (!window.atob || !window.Uint8Array) {
        // The current browser doesn't have the atob function. Cannot continue
        return null;
    }
    mimetype = mimetype || '';
    slicesize = slicesize || 512;
    var bytechars = atob(base64);
    var bytearrays = [];
    for (var offset = 0; offset < bytechars.length; offset += slicesize) {
        var slice = bytechars.slice(offset, offset + slicesize);
        var bytenums = new Array(slice.length);
        for (var i = 0; i < slice.length; i++) {
            bytenums[i] = slice.charCodeAt(i);
        }
        var bytearray = new Uint8Array(bytenums);
        bytearrays[bytearrays.length] = bytearray;
    }
    return new Blob(bytearrays, {type: mimetype});
}
