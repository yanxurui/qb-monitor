$(document).ready(function() {
    $rows = $('table > tbody > tr');
    $rows.each(function(index, e) {
        var s = new Date();
        $.ajax({
            url: '' + index,
            type: "GET",
            dataType: "json",

            success: function(data) {
                $(e).find("td:nth-child(2)").text(data['dl_info_speed'] || '-');
                $(e).find("td:nth-child(3)").text(data['dl_info_data'] || '-');
                $(e).find("td:nth-child(4)").text(data['up_info_speed'] || '-');
                $(e).find("td:nth-child(5)").text(data['up_info_data'] || '-');

                var seconds = Math.round((new Date() - s)/10)/100;
                console.log("Time elapsed: " + seconds + "seconds for " + index);
            },

            error: function(jqXHR, textStatus, errorThrown) {
                $(e).find("td:nth-child(2)").text('ERR');
                $(e).find("td:nth-child(3)").text('ERR');
                $(e).find("td:nth-child(4)").text('ERR');
                $(e).find("td:nth-child(5)").text('ERR');
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
