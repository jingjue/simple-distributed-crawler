(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-e9c6478a"],{"6fd9":function(e,t,a){"use strict";a.r(t);var i=function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticClass:"new-page",style:"min-height: "+e.pageMinHeight+"px"},[a("div",{staticClass:"create"},[a("el-button",{attrs:{size:"medium"},on:{click:function(t){e.createDialogVisible=!0}}},[e._v(" + 添加分布式设备")])],1),a("el-card",{staticStyle:{margin:"20px"}},[a("div",{staticClass:"table"},[a("el-table",{staticStyle:{width:"100%"},attrs:{data:e.tableData.slice((e.currentPage-1)*e.pageSize,e.currentPage*e.pageSize)}},[a("el-table-column",{attrs:{label:"设备地址","min-width":"100"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("span",{staticStyle:{"margin-left":"10px"}},[e._v(e._s(t.row.address))])]}}])}),a("el-table-column",{attrs:{prop:"ip",label:"设备IP","min-width":"100"}}),a("el-table-column",{attrs:{prop:"port",label:"端口号","min-width":"100"}}),a("el-table-column",{attrs:{prop:"username",label:"用户名","min-width":"100"}}),a("el-table-column",{attrs:{prop:"valid",label:"是否有效","min-width":"100"}}),a("el-table-column",{attrs:{label:"操作","min-width":"100"},scopedSlots:e._u([{key:"default",fn:function(t){return[a("el-button",{attrs:{size:"mini",type:"danger"},on:{click:function(a){return e.handleDelete(t.$index,t.row)}}},[e._v("删除 ")])]}}])})],1)],1)]),a("div",{staticClass:"clspage",staticStyle:{height:"35px",width:"100%"}},[a("el-pagination",{attrs:{align:"center",layout:"prev, pager, next","page-size":e.pageSize,"current-page":e.currentPage,total:e.total},on:{"current-change":e.handle_user_CurrentChange}})],1),a("div",{staticClass:"dialog"},[a("el-dialog",{attrs:{title:"新建设备",visible:e.createDialogVisible,width:"40%",center:""},on:{"update:visible":function(t){e.createDialogVisible=t}}},[a("span",[e._v("设备ip：")]),a("el-input",{attrs:{placeholder:"请输入ip"},model:{value:e.addDeviceInfor.ip,callback:function(t){e.$set(e.addDeviceInfor,"ip",t)},expression:"addDeviceInfor.ip"}}),a("span",[e._v("用户名：")]),a("el-input",{attrs:{placeholder:"请输入用户名"},model:{value:e.addDeviceInfor.username,callback:function(t){e.$set(e.addDeviceInfor,"username",t)},expression:"addDeviceInfor.username"}}),a("span",[e._v("密码：")]),a("el-input",{attrs:{placeholder:"请输入密码"},model:{value:e.addDeviceInfor.password,callback:function(t){e.$set(e.addDeviceInfor,"password",t)},expression:"addDeviceInfor.password"}}),a("span",[e._v("设备地址：")]),a("el-input",{attrs:{placeholder:"请输入设备地址"},model:{value:e.addDeviceInfor.address,callback:function(t){e.$set(e.addDeviceInfor,"address",t)},expression:"addDeviceInfor.address"}}),a("span",[e._v("端口号：")]),a("el-input",{attrs:{placeholder:"请输入端口号"},model:{value:e.addDeviceInfor.port,callback:function(t){e.$set(e.addDeviceInfor,"port",t)},expression:"addDeviceInfor.port"}}),a("span",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[a("el-button",{on:{click:function(t){e.createDialogVisible=!1}}},[e._v("取 消")]),a("el-button",{attrs:{type:"primary"},on:{click:e.createDevice}},[e._v("确 定")])],1)],1)],1)],1)},n=[],s=(a("7039"),a("5530")),r=a("2f62"),c=a("b775"),o=a("7424"),l={name:"proj_manage",i18n:a("ec6a"),data:function(){return{pageSize:7,currentPage:1,total:100,tableData:[],addDeviceInfor:{ip:"",username:"",password:"",address:"",port:"",valid:!0},addDevices:[],createDialogVisible:!1,editDialogVisible:!1,monitorDialogVisible:!1}},activated:function(){this.getAllDevices()},mounted:function(){this.getAllDevices()},methods:{getAllDevices:function(){var e=this;Object(c["e"])(o["DEVICE"],c["a"].POST,{project_name:""}).then((function(t){for(var a in e.tableData=[],t.data.message)e.tableData.push({address:t.data.message[a]["address"],ip:a,port:t.data.message[a]["port"],username:t.data.message[a]["username"],valid:t.data.message[a]["valid"]?"有效":"无效"});e.total=e.tableData.length}))},handleDelete:function(e,t){var a=this;this.$confirm("此操作将删除该分布式设备, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning",center:!0}).then((function(){Object(c["e"])(o["DEVICE_DEL_ADD"],c["a"].POST,{cover:!1,add_devices:[],rm_devices:[t.ip]}).then((function(e){0!=Object.getOwnPropertyNames(e.data.rm_error).length?a.$message({message:"删除失败",type:"warning"}):(a.createDialogVisible=!1,a.$message({message:"删除成功",type:"success"}),a.getAllDevices())}))})).catch((function(){a.$message({type:"info",message:"已取消删除"})}))},handle_user_CurrentChange:function(e){this.currentPage=e},createDevice:function(){var e=this;if(""==this.addDeviceInfor.port||""==this.addDeviceInfor.username||""==this.addDeviceInfor.password||""==this.addDeviceInfor.address||""==this.addDeviceInfor.ip)this.$message({message:"请输入完整信息",type:"warning"});else{var t=[this.addDeviceInfor];Object(c["e"])(o["DEVICE_DEL_ADD"],c["a"].POST,{cover:!1,add_devices:t,rm_devices:[]}).then((function(t){0!=Object.getOwnPropertyNames(t.data.add_error).length?e.$message({message:"设备ip重复，创建失败",type:"warning"}):(e.createDialogVisible=!1,e.$message({message:"新建分布式设备成功",type:"success"}),e.getAllDevices())}))}}},computed:Object(s["a"])(Object(s["a"])({},Object(r["d"])("setting",["pageMinHeight"])),{},{desc:function(){return this.$t("description")}})},d=l,p=(a("a9d7"),a("2877")),u=Object(p["a"])(d,i,n,!1,null,"7da8b7e2",null);t["default"]=u.exports},7039:function(e,t,a){var i=a("23e7"),n=a("d039"),s=a("057f").f,r=n((function(){return!Object.getOwnPropertyNames(1)}));i({target:"Object",stat:!0,forced:r},{getOwnPropertyNames:s})},"7dde":function(e,t,a){},a9d7:function(e,t,a){"use strict";var i=a("7dde"),n=a.n(i);n.a},ec6a:function(e,t){e.exports={messages:{CN:{content:"演示页面",description:"这是一个演示页面"},HK:{content:"演示頁面",description:"這是一個演示頁面"},US:{content:"Demo Page",description:"This is a demo page"}}}}}]);