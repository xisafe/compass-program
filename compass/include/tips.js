var tips = (function(){
	
	// ele 需要提示框的元素
	// options 自定义参数
	var Tip = function(ele,opts){
		this.ele = ele
		this.$ele = this.select(ele)
		var obj = {}
		typeof opts !== 'object' ? opts = {} : ''
		/*******读取用户设定参数，参数合法则替换默认值******/
		for(var key in Tip.DEFAULTS){
			if (typeof Tip.DEFAULTS[key] !== 'object') {
				if (key === 'position' && opts.position) {
					opts.position = opts.position.toLowerCase()
					opts.position = opts.position.length === 1?/l|r/.test(opts.position) ?
					opts.position+'b' : /t|b/.test(opts.position) ? opts.position+'r' :'lb':opts.position
				}
				obj[key] = !/triangle|close|drag/.test(opts[key]) && typeof opts[key] !== 'undefined' ?
				opts[key] : Tip.DEFAULTS[key]
			}else{
				obj[key] ={}
				if (opts[key]) {
					for(var btn_key in Tip.DEFAULTS[key]){
						if (typeof Tip.DEFAULTS[key][btn_key] !== 'object') {
							obj[key][btn_key] = typeof opts[key][btn_key] !== 'undefined' ?
							opts[key][btn_key] : Tip.DEFAULTS[key][btn_key]
						}else{
							obj[key]['custom'] = opts[key]['custom'] ? opts[key]['custom'] : ''
						}
					}
				}else{
					obj[key] = Tip.DEFAULTS[key]
				}
			}
		}
		var custom = obj.btn.custom
		if(custom instanceof Array){
			for(var i=0;i<custom.length;i++){
				custom[i].id ? custom[i].id+='_'+obj.id : custom[i]['id'] = obj.id+'_cus'
			}
		} 
		/*************参数设定结束**************/

		this.opts = obj

		// 元素id
		this.ids = {
			wrap:this.opts.id,
			cancle: this.opts.id+'_cancel',
			close:this.opts.id+'_close',
			triangle:this.opts.id+'_triangle'
		}	
	}

	Tip.prototype = {
		// 初始化
		init : function(){
			this.buildHTML();
			this.setCSS();
			this.bindEvenet();
		},
		// 创建DOM
		buildHTML : function(){
			var opts = this.opts
			var ids = this.ids
			var html = ''

			html += '<div class="tip" id="'+ids.wrap+'" >'
			opts.close ? html += '<b class="close" id="'+ids.close+'">x</b>':'' 
			html += '<div class="tip-cont">'
			opts.title ? html += '<div class="tip-title">'+opts.title+'</div>' :''
			html += '<div class="tip-text">'+opts.content+'</div>'
			var btn = opts.btn
			if (btn.cancel || btn.custom instanceof Array) {
				html += '<div class="tip-button">'
				btn.cancel ?  html += '<button class="cancel" id="'+ids.cancle+'">已阅</button>' :''
				if(btn.custom instanceof Array){
					for(var i=0;i<btn.custom.length;i++){
						html += this.createCustomBtn(btn.custom[i])
					}
				}
				html += '</div>' 
			}
			html += '</div>'
			opts.triangle ? html += '<b class="in" id="'+ids.triangle+'"></b>' :''
			html += '</div>'
			var ele_parent = this.$ele.parentElement
			ele_parent.innerHTML += html
		},
		// 改变CSS
		setCSS : function(){
			var opts = this.opts
			var ids = this.ids
			var tip_cont = this.select(opts.id+' .tip-cont')

			if (opts.adjust) {this.setStyle(tip_cont,opts.adjust)}	
			
			this.setPosition()
			var position = opts.position.split('')
			if (opts.triangle) {
				var triangle = this.select(ids.triangle)
				var pos_sty = {
					l:['20px','','','-15px','10px 0px 10px 15px','transparent #a0d3e8 transparent'],
					r:['20px','','-15px','','10px 15px 10px 0px','transparent #a0d3e8 transparent'],
					b:['-15px','','20px','','0px 10px 15px 10px','#a0d3e8 transparent'],
					t:['','-15px','20px','','15px 10px 0px 10px','#a0d3e8 transparent']
				}

				this.controlTriangle(triangle,pos_sty[opts.position[0]])

				position[1] === 't' && /l|r/.test(position[0]) && b_a('top','bottom')
				position[1] === 'l' && /t|b/.test(position[0]) && b_a('left','right')

				function b_a(a,b) {
					triangle.style[a] = [triangle.style[b],triangle.style[b]=triangle.style[a]][0]
				}
			}

			if (opts.color) {
				this.setStyle( this.select(ids.wrap),{'backgroundColor':opts.color})
				if (opts.triangle) {
					var triangle_color = triangle.style.borderColor.replace(/rgb\(.*\)/,opts.color)
					this.setStyle( this.select(ids.triangle),{'borderColor':triangle_color})
				}
			}

			
		},
		// 绑定事件
		bindEvenet : function(){
			var opts = this.opts
			var ids = this.ids
			var $ele = this.$ele

			opts.trigger === 'click' && this.controlTip(this.select(this.ele),'show')
			opts.trigger === 'hover' && this.controlTip(this.select(this.ele),'show','mouseenter')
			opts.close && this.controlTip(this.select(ids.close),'hide')
			opts.btn.cancel && this.controlTip(this.select(ids.cancle),'hide')
			var btn_cus = opts.btn.custom
			if (btn_cus instanceof Array) {
				for(var i=0;i<btn_cus.length;i++){
					btn_cus[i].fn && this.on(this.select(btn_cus[i].id),'click',btn_cus[i].fn)
				}
			}
			if (opts.drag) {
				this.select(ids.wrap+' .tip-text').className += ' draggable'
				this.drag(this.select(ids.wrap))
				
			}
		},
		// 创建自定义底部按钮
		// btn_config  每个自定义底部按钮对象
		createCustomBtn:function(btn_config){
			var btn_config = btn_config
			var btn = '<button '

			for(var key in btn_config){
				if (key !== 'fn' && key !== 'text') {
					btn += key
					btn += '="'+btn_config[key]+'" '
				}
			}
			btn = btn + '>' +btn_config.text + '</button>'
			return btn
		},
		// 控制tip面板的隐藏与显示
		// ele  触发控制面板的元素
		// status  隐藏或显示 'show' or other
		// type  触发方式 hover or click
		controlTip:function(ele,status,type){
			var self = this
			type = type || 'click'
			status = status === 'show' ? 'block' : 'none'
			var $tip = self.select(self.opts.id)
			this.on(ele,type,function(){
				$tip.style.display = status
				status === 'block' && self.setPosition()
			})
			type === 'mouseenter' && this.controlTip(ele,'hide','mouseleave')

		},
		// 控制面板三角的样式
		// ele 元素
		// style_arr:[t,b,l,r,bw,bc]
		controlTriangle:function (ele,style_arr) {
			var arr = ['top','bottom','left','right','borderWidth','borderColor']
			var obj = {}
			for (var i = 0; i < style_arr.length; i++) {
				if(style_arr[i]){
					obj[arr[i]] = style_arr[i]
				}  
			}
			this.setStyle(ele,obj)
		},
		setPosition:function(){
			var ele = this.select(this.ele)
			var position = this.opts.position

			var ele_position = this.getPosition(ele)
			var ele_size = {w:this.getStyle(ele,'width'),h:this.getStyle(ele,'height')}
			var wrap_size = {
				w:this.getStyle(this.select(this.ids.wrap),'width').replace(/px/,''),
				h:this.getStyle(this.select(this.ids.wrap),'height').replace(/px/,'')
			}
			var triangle_size = 16
			var ele_pos_obj = {
				'rb':{
					left:ele_position.left+ele_size.w+triangle_size,
					top:ele_position.top
				},
				'rt':{
					left:ele_position.left+ele_size.w+triangle_size,
					top:ele_size.h+ele_position.top-wrap_size.h
				},
				'br':{
					left:ele_position.left,
					top:ele_size.h+triangle_size+ele_position.top
				},
				'bl':{
					left:ele_position.left+ele_size.w-wrap_size.w,
					top:ele_size.h+triangle_size+ele_position.top
				},
				'lb':{
					left:ele_position.left-wrap_size.w-triangle_size,
					top:ele_position.top
				},
				'lt':{
					left:ele_position.left-wrap_size.w-triangle_size,
					top:ele_position.top-wrap_size.h+ele_size.h
				},
				'tl':{
					left:ele_position.left+ele_size.w-wrap_size.w,
					top:ele_position.top-wrap_size.h-triangle_size
				},
				'tr':{
					left:ele_position.left,
					top:ele_position.top-wrap_size.h-triangle_size
				},
			}
			
			if(ele_pos_obj[position]){
				var add_t = this.opts.move.top ? this.opts.move.top:0
				var add_l = this.opts.move.left ? this.opts.move.left:0
				this.setStyle(this.select(this.ids.wrap),{
					'top':(ele_pos_obj[position].top-add_t)+'px',
					'left':(ele_pos_obj[position].left-add_l)+'px'
				})
			}
		},
		drag:function(ele){
			var self = this
			var dragNode = (ele.querySelector(".draggable") || ele);
	        this.on(dragNode, "mousedown", function (event) {
	            var dragElement = draggableConfig.dragElement = new DragElement(ele);

	            draggableConfig.mouse.setXY(event.clientX, event.clientY);
	            draggableConfig.dragElement
	                .setXY(dragElement.target.style.left, dragElement.target.style.top)
	                .setTargetCss({
	                    "zIndex": draggableConfig.zIndex++
	                    // ,"position": "absolute"
	                });
	        }).on(dragNode, "mouseover", function () {
	            self.setStyle(this, draggableStyle.dragging);
	        }).on(dragNode, "mouseout", function () {
	            self.setStyle(this, draggableStyle.defaults);
	        });
	        this.move()
	        
		},
		move:function(){
			var self = this

			this.on(document, "mousemove", move);
		    this.on(document, "mouseup", function (event) {
		        draggableConfig.dragElement = null;
		    })
			function move(event){
				if (draggableConfig.dragElement) {
		            var mouse = draggableConfig.mouse,
		                dragElement = draggableConfig.dragElement;
		            dragElement.setTargetCss({
		                "left": parseInt(event.clientX - mouse.x + dragElement.x) + "px",
		                "top": parseInt(event.clientY - mouse.y + dragElement.y) + "px"
		            });

		            self.off(document, "mousemove", move);
		            setTimeout(function () {
		                self.on(document, "mousemove", move);
		            }, 25);
		        }
			}
			
		},
		getPosition:function(ele){
			var actualLeft = ele.offsetLeft,
		    	actualTop = ele.offsetTop,
		    	current = ele.offsetParent
		    while (current !== null) {　　　　
		        actualLeft += current.offsetLeft　　　　
		        actualTop += current.offsetTop　　　
		        current = current.offsetParent　　
		    }
		    if (document.compatMode == "BackCompat") {　　　　
		        var elementScrollLeft = document.body.scrollLeft　　　　
		        var elementScrollTop = document.body.scrollTop
		    } else {　　　　
		        var elementScrollLeft = document.documentElement.scrollLeft　　　　
		        var elementScrollTop = document.documentElement.scrollTop
		    }
		    return {
		        left: actualLeft - elementScrollLeft,
		        top: actualTop - elementScrollTop
		    }
		},
		getStyle:function(node,styleName){
			var realStyle = null;
			if (window.getComputedStyle) {
			    realStyle = window.getComputedStyle(node, null)[styleName]    // 非IE
			} else { 
			    realStyle = node.currentStyle[styleName]  // IE
			}
			return realStyle
		},
		// 改变样式
		// node 目标元素
		// style 需要改变的样式名
		// val 需要改变的值
		setStyle:function (node,css) {

			for (var key in css) {
				// var cssValue = css[key].splits
                if(typeof node.style[key] !== 'undefined') node.style[key] = css[key];
            }
            return this;
		},
		// 选择器
		select:function (node) {
			node = /^\#/.test(node) ? node : '#'+node 
			return document.querySelector(node)
		},
		// 绑定事件
		on:function(node,eventName,handler){
			if (node.addEventListener) {
                node.addEventListener(eventName, handler);
            }
            else {
                node.attachEvent("on" + eventName, handler);
            }
            return this;
		},
		off: function (node, eventName, handler) {
            if (node.removeEventListener) {
                node.removeEventListener(eventName, handler);
            }
            else {
                node.detachEvent("on" + eventName, handler);
            }
            return this;
        },
	}
	//#region 拖拽元素类
    function DragElement(node) {
        this.target = node;

        node.onselectstart = function () {
            //防止拖拽对象内的文字被选中
            return false;
        }
    }
    DragElement.prototype = {
        constructor: DragElement,
        setXY: function (x, y) {
            this.x = parseInt(x) || 0;
            this.y = parseInt(y) || 0;
            return this;
        },
        setTargetCss: function (css) {
            this.setStyle(this.target, css);
            return this;
        },
        setStyle:function (node,css) {
			for (var key in css) {
                if(typeof node.style[key] !== 'undefined') node.style[key] = css[key];
            }
            return this;
		},
    }
    //#endregion

    //#region 鼠标元素
    function Mouse() {
        this.x = 0;
        this.y = 0;
    }
    Mouse.prototype.setXY = function (x, y) {
        this.x = parseInt(x);
        this.y = parseInt(y);
    }
    //#endregion

    //拖拽配置
    var draggableConfig = {
        zIndex: 1,
        dragElement: null,
        mouse: new Mouse()
    };

    var draggableStyle = {
        dragging: {
            cursor: "move"
        },
        defaults: {
            cursor: "default"
        }
    }
	// 默认值
	Tip.DEFAULTS = {
		id:'Tip',
		trigger:'hover',
		color:'',
		title:false,
		triangle:true,
		drag:false,
		content:'请填入您的内容，属性名为content',
		close:false,
		position:'lb', //l r t b 
		move:{
			left:0,
			top:0
		},
		adjust:{},
		btn:{
			cancel:false,
			custom:''
		}
	}
	// 单例模式：第一次实例化一次将其保存下来，后面用的时候将保存下来的继续用
	var init = function(ele,opts){
		var $ele = document.querySelector(ele),
			tips = $(ele).data('tips')
		if(!tips){
			tips = new Tip(ele,typeof opts === 'object' && opts)
			$(ele).data('tips',tips)
		}
		tips.init()
	}

	return {
		init:init
	}
})()