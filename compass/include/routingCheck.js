setTimeout(function(){
	$('#add-div-content').children('form').attr('name','routing_form')
	
	var check = new ChinArk_forms
	var obj = {
		'form_name':'routing_form',
		'option':{
			'source':{
				'type':'text',
				'required':'0',
				'check':'ip|ip_mask'
			},
			'destination':{
				'type':'text',
				'required':'0',
				'check':'ip|ip_mask'
			},
			'gw':{
				'type':'text',
				'required':'1',
				'check':'other',
				'other_reg':'/^([1-9]|[1-9]\\d|1\\d{2}|2[0-1]\\d|22[0-3])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}$/'
			},
			'metric':{
				'type':'text',
				'required':'1',
				'check':'num',
		        ass_check:function(eve){
	                var msg=""
	                var metric = eve._getCURElementsByName("metric","input","routing_form")[0].value
	                if (metric<0 || metric>Math.pow(2,32)) {
	                	msg = 'Metric值必须在0-4294967296之间！'
	                }
	                return msg
	            }
			},
			'remark':{
				'type':'text',
				'required':'0',
				'check':'note'
			}
		}

	}
	check._main(obj)
},0)

function clear_gw(){
	if ($('select[name="via_type"]').val()==='gw' && /[a-zA-Z]/.test($('input[name="gw"]').val()) ) {
		$('input[name="gw"]').val('')
	}
}