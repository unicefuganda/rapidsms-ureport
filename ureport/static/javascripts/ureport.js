
function load_polls()
{

    $('#polls').load('/ureport/polls/');
}

function load_tag_cloud()
{
        var id_list="";
        $("#poll_list").find('input').each(function(){

                 if($(this).attr("checked"))
                    {

                           id_list=id_list+'+'+String(this.id);
                    }

        });

    var url="/ureport/tag_cloud/"+"?pks=" +id_list;

    $('#tag_cloud').load(url);
}


 $(document).ready(function() {

        load_polls();


      });