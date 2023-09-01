var dates = []
var dateIndex = -1
var curDate = "无数据"
var pattern = /\[.+\/(.+\/.+)\].*\((Information|Critical|Serious|Warning)\)(.+)/

window.onload = function(){
	getBaseInfo(true)
}

var timer = setInterval(function() {
	var hours = new Date().getHours();
	var min = new Date().getMinutes();
	console.log(hours, min)
	if(hours == '3' && min=='0'){
		getBaseInfo(true)	
	}
}, 50000)

// date list
function getBaseInfo(load){
	axios.get('/api/getbaseinfo')
		.then(function (response) {
			$('#maintitle').text(response.data.title)
			dates = response.data.datelist
			for(var i = 0; i < dates.length; i++){
				console.log(dates[i])
			}
			if(load && dates.length){
				pagVue.selectDate(0)
			}
		})
		.catch(function (error) {
			alert(error);
		});
}

var resultVue = new Vue({
	delimiters: ['[[', ']]'],
	el:'#result',
	data: {
		results: [""],
		tmpResults: [""]
	},
	methods:{
		getDayResult:function(){
			axios.get('/api/getresults',{
				params:{
					date: curDate,
				}
			})
			.then(response => (this.tmpResults = response.data.errorlist))
			.catch(function (error) { 
				console.log(error);
			});
		},
		getAllResult:function(){
			axios.get('/api/getallresults')
				.then(response => (this.tmpResults = response.data.errorlist))
			.catch(function (error) { 
				console.log(error);
			});
		}
	},
	watch:{
		tmpResults: function (value) {
			$('#tabletable').bootstrapTable('removeAll')

			if(!value){
				console.log("tmpResults null")
				return
			}
			
			var rows = []

			for (i = 0; i < value.length; ++i){
				value[i].file = value[i].file + ':' + value[i].line
				rows.push(value[i])
			}

			console.log(rows)
			$('#tabletable').bootstrapTable('load', rows)
		}
	}
});

var optionVue = new Vue({
	delimiters: ['[[', ']]'],
	el:'#option',
	data: {
		selected: '昨日新增'
	},
	methods:{
		makeSelect:function(value){
			if(value == 1){
				this.selected = "昨日新增";
				$("#zuori").addClass("active");
				$("#quanbu").removeClass("active");
				pagVue.selectDate(0)
				$("#pag").show();
			}
			else if(value == 2){
				this.selected = "全部";
				$("#quanbu").addClass("active");
				$("#zuori").removeClass("active");
				resultVue.getAllResult()
				$("#pag").hide();
			}
		}
	}
});

var pagVue = new Vue({
	delimiters: ['[[', ']]'],
	el:'#pag',
	data:{
		date : curDate,
		disable : 0
	},
	methods:{
		selectDate:function(value){
			this.disable = 0
			if(dates.length == 0)
				return
			if(value == 0){
				dateIndex = dates.length - 1
			}
			else if(value > 0){
				if(dateIndex < dates.length - 1)
					dateIndex += 1
			}
			else if(value < 0){
				if(dateIndex > 0)
					dateIndex -= 1
			}
			if(dateIndex < dates.length){
				curDate = dates[dateIndex]
				this.date = curDate
				resultVue.getDayResult()
			}
			if(dateIndex == 0)
				this.disable += 1
			if(dateIndex == dates.length - 1)
				this.disable += 2
		}
	}
});


$(document).ready(function () {
	$('#tabletable').bootstrapTable();
});

function cellStyle(value, row, index) {
	var classes = [
		'bg-blue',
		'bg-green',
		'bg-orange',
		'bg-yellow',
		'bg-red'
	]

	if (value == 'Warning') {
		return {
			classes: "table-warning"
		}
	}
	if (value == 'Critical') {
		return {
			classes: "table-danger"
		}
	}
	if (value == 'Serious') {
		return {
			classes: "table-info"
		}
	}
	if (value == 'Information') {
		return {
			classes: "table-success"
		}
	}
	return {
	}
}

function normalcellStyle(value, row, index) {
	return {
		css: {
			style:"word-wrap:break-word; word-break:break-all"
		}
	}
}

function dangerLevelSorter(a, b) {
	const dangerLevels = ["Critical", "Serious", "Warning", "Information"];

	const indexA = dangerLevels.indexOf(a);
	const indexB = dangerLevels.indexOf(b);

	if (indexA < indexB) {
		return -1;
	}
	if (indexA > indexB) {
		return 1;
	}
	return 0;
}

function operateFormatter(value, row, index) {
	return [
		'<button class="btn btn-secondary btn-sm btn-action" data-bs-toggle="modal" data-bs-target="#codeModal" style="width:80px">查看代码</button>',
		'<button class="btn btn-secondary btn-sm btn-copy" style="width:80px">复制路径</button>'
	].join('')
}

window.operateEvents = {
	'click .btn-action': function (e, value, row, index) {
		// alert(row.content)
		$('#dialog-text').text(row.content)
	},
	'click .btn-copy': function (e, value, row, index) {
		// alert(row.file)
		// 创建一个新的 textarea 元素，设置内容为要复制的文本
		const textarea = document.createElement("textarea");
		textarea.value = row.file;

		// 将 textarea 添加到文档中
		document.body.appendChild(textarea);

		// 选中 textarea 内容
		textarea.select();

		// 复制选中的内容到剪贴板
		document.execCommand("copy");

		// 移除临时创建的 textarea
		document.body.removeChild(textarea);

		// 修改按钮文本提示用户复制成功
		e.target.innerText = "已复制";
		setTimeout(() => {
			e.target.innerText = "复制路径";
		}, 2000); // 2秒后恢复按钮文本
	}
}