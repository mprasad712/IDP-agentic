var iCnt = 0;

function addfield(type, fieldName, customtype) {

  var fieldName = fieldName;
  errorMsg = ""
  iCnt = iCnt + 1;
  var field_dynamic_id = fieldName.replace(' ', '_').toLowerCase();
  var field_dynamic_display = fieldName.replace('_', ' ');
  if ($('#idp_user_form  #' + field_dynamic_id).length)         // use this if you are using id to check
  {
    errorMsg = 'Field ' + field_dynamic_display + ' already exist';

  }
  else {
    var fieldElementString = '<div class="form-group row additem  ui-sortable" style = "cursor: move;" id=tb' + iCnt + ' title="drag"> <span style="margin-top:4px; font-size:9px" class="col-sm-1 handle ui-sortable-handle"><i class="fa fa-align-justify" style="margin-bottom: 0;font-size: 15px;line-height: 1.5;color:#808080;"></i></span>'
    fieldElementString += '<label class="grabbable col-sm-3 col-form-label stan-label" style="white-space: normal;" for="' + field_dynamic_display + '">' + field_dynamic_display + '</label>';
    fieldElementString += '<div class="col-sm-8">'
    fieldElementString += '<div class="close-btn-wrap grabbable" style="display: inline-flex;width: 100%;"><input class="form-control stan-input" id="' + field_dynamic_id + '" dataholder="' + type + '" customtype ="' + customtype + '" type="text" aria-describedby="nameHelp" placeholder="' + field_dynamic_display + '"    readonly="readonly"  >';
    if (field_dynamic_id != 'file_name') { fieldElementString += '<div class="close-btn" style="margin-left:10px;line-height:32px;cursor:pointer;color:#808080;padding-top:5px;" onclick="btnclose(' + iCnt + ')"><i class="fa fa-trash"></i></div>'; }
    fieldElementString += '</div></div>'
    fieldElementString += '</div> '

  }
  if (errorMsg) {
    //alert(errorMsg);
  }

  if (customtype == '') {
    $('#stfield input:checkbox').prop('checked', false);
  }
  else {
    $("#custom_field_input").removeClass("redalert");
    $("#custom_field_datatype").removeClass("redalert");

    $("#custom_field_input").val("");
    $('#custom_field_datatype').val("0").attr("selected", "selected");


  }


  $("#entity-form").append(fieldElementString);
  $('#NewField').val('');


}



function generate_table_template(staticTableData, dynamicTableData) {

  console.log(dynamicTableData)
  console.log(staticTableData)
  var header = ""
  iCnt = iCnt + 1;
  for (var tablerow_start = 0; tablerow_start <= (staticTableData.length - 1); tablerow_start++) {
    var header_name = ''; var header_array = '';
    header_array = staticTableData[tablerow_start].split("|");
    header_name = uc_first(header_array[0].replace('_', ' '));
    var header_row = "<th tabindex='0' class='sorting_asc' aria-controls='example2' datavalue='" + staticTableData[tablerow_start] + "' datatype= 'static' aria-label='Rendering engine: activate to sort column descending' aria-sort='ascending' rowspan='1' colspan='1'>" + header_name + "</th>"

    header += header_row
  }

  table_header_row = "<tr role='row' id='tb" + iCnt + "'>" + header + "</tr>"


  for (var tablerow_start = 0; tablerow_start <= (dynamicTableData.length - 1); tablerow_start++) {
    var header_dyn_name=''; var header_dyn_array='';
    header_dyn_array= dynamicTableData[tablerow_start].split("|");
    header_dyn_name=uc_first(header_dyn_array[0].replace('_', ' '));
    var header_row = "<th tabindex='0' class='sorting_asc' aria-controls='example2' datavalue='"+ dynamicTableData[tablerow_start] +"' datatype= 'cust' aria-label='Rendering engine: activate to sort column descending' aria-sort='ascending' rowspan='1' colspan='1'>" + header_dyn_name + "</th>"

    header += header_row
  }
  header += '<th onclick="btnclose(' + iCnt + ')"><i class="fas fa-trash"></i></th>'
  table_header_row = "<tr role='row' id='tb" + iCnt + "'>" + header + "</tr>"

  $('#table_heading').html(table_header_row)
}


/****************************** Add Standard Fields **********************/

$("#save-stdfield-button").click(function (event) {
  event.preventDefault();
  var searchIDs = $("#stfield input:checkbox:checked").map(function () {

    return $(this).attr("id");
  }).get();
  searchIDs.forEach(function (item) {
    console.log(item)
     
    data_type = $("#"+item).attr("data_type")
    
    addfield('stan', item, data_type);
  });
});

/****************************** Add Custom Fields **********************/

$('#add-custom-static').click(function () {
  var fieldName = $('#custom_field_input').val();
  var fieldType = $('#custom_field_datatype').val();


  $("#custom_field_input").removeClass("redalert");
  $("#custom_field_datatype").removeClass("redalert");

  if (fieldName == '') {

    $("#custom_field_input").focus();
    $("#custom_field_input").addClass("redalert");
  }
  else if (fieldType == 0) {

    $("#custom_field_datatype").focus();
    $("#custom_field_datatype").addClass("redalert");
  } else {
    addfield('cust', fieldName, fieldType);
  }


});
function uc_first(input) {
  var words = input.split(' ');
  output = ""
  for (var i = 0; i < words.length; i++) {
    output = output + " " + words[i].substr(0, 1).toUpperCase() + words[i].substr(1);
  }
  return output.substr(1)
}
/****************************** Add Table Data Row **********************/

$("#add-standard-dynamic").click(function (event) {
  event.preventDefault();
  var dynamic_lavel = $("#dynamic_field_checkbox input:checkbox:checked").map(function () {
    var last_key='';
    last_key=$(this).attr("id");
    return $(this).attr("id")+'|'+$('#'+last_key+'_value').val(); 
  }).get();
  dynamic_custom_lavel = []
  //final_dynamic_list= dynamic_lavel.concat(dynamic_custom_lavel)
  generate_table_template(dynamic_lavel, dynamic_custom_lavel)
});


$("#add-custom-dynamic").click(function (event) {
  event.preventDefault();
  var dynamic_lavel = $("#dynamic_field_checkbox input:checkbox:checked").map(function () {
    var last_key='';
    last_key=$(this).attr("id");
    if($('#'+last_key+'_value').val() == "")
    {
      return $(this).attr("id")+'|'+ $(this).attr("id").replace("_"," ");
    }
    else{
      return $(this).attr("id")+'|'+$('#'+last_key+'_value').val();
    }
    

  }).get();

  var dynamic_custom_lavel = $("#dynamic_field_input input:text").map(function () {
    if ($(this).val() != "") {
      return $(this).val().replace(' ', '_').toLowerCase() +'|'+$(this).val();

    } else {
      alert("Please enter custom fields name")
    }

  }).get();
  console.log(dynamic_custom_lavel)
  //final_dynamic_list= dynamic_lavel.concat(dynamic_custom_lavel)
  generate_table_template(dynamic_lavel, dynamic_custom_lavel)
});


/*********************** Remove  field code start ********************/
function btnclose(id) {
  var custumField = confirm("Are you sure to delete this field?");
  if (custumField == true) {
    $("#tb" + id).remove();
  }
}

/*********************** Remove  field code finish ********************/


/*********************** Create Idp Form ********************/

$("#launch-idp").click(function (event) {

  
  

  var config_name = $('#config_name').val().trim()
  if (config_name != '') {


    var standard_dict = []
    var custom_dict = []
    var custom_dict_mapping = []
    var table_static_dict = []
    var table_custom_dict = []
    var custom_dict_datatype = []
    var table_custom_fields_mapping_name = []
    var order_count = 1
    var tblcpount = 1

    var datatype_custom_dict = []
    var datatype_standard_dict = []
    $("form#idp_user_form :input").each(function () {
      //standard_dict.push($(this).attr('id')); 



      if ($(this).attr('dataholder') == "cust") {
        datatype_custom_dict.push($(this).attr('id')+ "|" + $(this).attr('customtype'))
        custom_dict.push($(this).attr('id'));
        custom_dict_datatype.push($(this).attr('customtype'))
        
        custom_dict_mapping.push("s_" + parseInt(order_count) );
        order_count = order_count + 1
      }
      else {
        standard_dict.push($(this).attr('id'));
        datatype_standard_dict.push($(this).attr('id') + "|"+$(this).attr('customtype'))
      }

    });

    $('thead#table_heading th').each(function () {

      if ($(this).attr('datatype') == "static") {
        var thdata = $(this).attr('datavalue');
        if (thdata != '') { table_static_dict.push(thdata); }

      }
      if ($(this).attr('datatype') == "cust") {
        var thdata = $(this).attr('datavalue');
        if (thdata != '') 
        { 
          table_custom_dict.push(thdata); 
          table_custom_fields_mapping_name.push("t_" + parseInt(tblcpount));
          tblcpount = tblcpount + 1
        
        }
      }

    }); 

    
    var check_file_name = standard_dict.indexOf('file_name');
    

    var dataDict = { 'config_name': $('#config_name').val(), 'standard_dict': standard_dict, 'custom_dict': custom_dict, 'table_static_dict': table_static_dict, 'table_custom_dict': table_custom_dict, 'custom_dict_mapping': custom_dict_mapping, 'custom_dict_datatype': custom_dict_datatype,'table_custom_fields_mapping_name' : table_custom_fields_mapping_name,'datatype_custom_dict' : datatype_custom_dict, 'datatype_standard_dict':datatype_standard_dict }
    //console.log(custom_dict)
    if(check_file_name==0){
      add_fields_configuration(dataDict)
    }else{
      toastr.error("File Name is required to generate configuration.")
    }
    


  } else {
    $("#config_name").focus()
    $("#config_name").attr("style", "border:solid 1px red !important;")
  }

});
