//~ $( function(){

    //~ API
    function NewScan(){
        $('.js_scanner_status').html(
            '<div class="status">Идёт сканирование: <b class="js_prc">0</b>%<br></div>'
        );
        prc_show();
        $.ajax({
            url: '/api/scan',
            type: 'GET',
            cache: false,
            success: function(data) {
                if (data=='1'){ // всё отработало хорошо
                    $('.js_scanner_status').html('');
                }
                ShowFiles();
            }
        });
    }

    function RmFiles(){
        if (window.confirm('Хотите удалить все сохранённые сканы файлов с сервера?')) {
            $('.js_scanner_status').html('Удаляем файлы');
            $.ajax({
                url: '/api/rm_files',
                type: 'GET',
                cache: false,
                success: function() {
                    $('.js_scanner_status').html('Файлы удалены');
                    ShowFiles();
                }
            });
        }
    }

    function ShowFiles(){
        $.ajax({
            url: '/api/files',
            type: 'GET',
            cache: false,
            success: function(data) {
                $('.js_scanner_files').html(data);
                lightbox();
            }
        });
    }

    //~ прогресс сканирования
    function prc_show(){
        var max_seconds = 60;
        var count = 0;
        var counter = setInterval(timer, 1000);
        function timer(){
          count=count+1;
          if (count >= max_seconds){
             clearInterval(counter);
             $('.js_prc').html(100);
             return;
          }
          $('.js_prc').html(Math.round(100*count/max_seconds));
        }
    }


    //~ IMG
    //~ https://github.com/marekdedic/imagelightbox
    function lightbox(){
        $('.js_scanner_files').find('img').parent().imageLightbox({
            overlay: true,
            button: true,
            quitOnDocClick: true,
            navigation: true
        });
    }
    lightbox();

//~ });
