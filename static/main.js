$(document).ready(function() {
    $rows = $('table > tbody > tr');
    $rows.each(function(index, e) {
        var s = new Date();
        $.ajax({
            url: '/' + index,
            type: "GET",
            dataType: "json",

            success: function(data) {
                if (data.hasOwnProperty('dl_info_speed')) {
                    $(e).find("td:nth-child(2)").text(data['dl_info_speed'] + '/s' + '(' + data['dl_info_data'] + ')');
                    $(e).find("td:nth-child(3)").text(data['up_info_speed'] + '/s' + '(' + data['up_info_data'] + ')');
                } else {
                    $(e).find("td:nth-child(2)").text('-');
                    $(e).find("td:nth-child(3)").text('-');
                }

                var seconds = Math.round((new Date() - s)/10)/100;
                console.log("Time elapsed: " + seconds + "seconds for " + index);
            },

            error: function(jqXHR, textStatus, errorThrown) {
                console.log('jqXHR:');
                console.log(jqXHR);
                console.log('textStatus:');
                console.log(textStatus);
                console.log('errorThrown:');
                console.log(errorThrown);
            },
        });  
    });
});
