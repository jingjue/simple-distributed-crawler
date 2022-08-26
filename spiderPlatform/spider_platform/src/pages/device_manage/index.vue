<template>
  <div class="new-page" :style="`min-height: ${pageMinHeight}px`">
    <div class="create">
      <el-button size="medium" @click="createDialogVisible=true"> + 添加分布式设备</el-button>
    </div>
    <el-card style="margin: 20px">
       <div class="table">
      <el-table
          :data="tableData.slice((currentPage-1)*pageSize,currentPage*pageSize)"
          style="width: 100%">
        <el-table-column
            label="设备地址"
            min-width="100">
          <template slot-scope="scope">
            <span style="margin-left: 10px">{{ scope.row.address }}</span>
          </template>
        </el-table-column>
        <el-table-column
            prop="ip"
            label="设备IP"
            min-width="100">
        </el-table-column>
        <el-table-column
            prop="port"
            label="端口号"
            min-width="100">
        </el-table-column>
        <el-table-column
            prop="username"
            label="用户名"
            min-width="100">
        </el-table-column>
        <el-table-column
            prop="valid"
            label="是否有效"
            min-width="100">
        </el-table-column>
        <el-table-column
            label="操作"
            min-width="100">
          <template slot-scope="scope">
            <el-button
                size="mini"
                type="danger"
                @click="handleDelete(scope.$index, scope.row)">删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    </el-card>

    <div style="height:35px;width:100%" class="clspage">
      <el-pagination align='center' @current-change="handle_user_CurrentChange" layout="prev, pager, next"
                     :page-size="pageSize" :current-page="currentPage" :total="total"></el-pagination>
    </div>
    <div class="dialog">
      <el-dialog
          title="新建设备"
          :visible.sync="createDialogVisible"
          width="40%"
          center>
        <span>设备ip：</span>
        <el-input v-model="addDeviceInfor.ip" placeholder="请输入ip"></el-input>
        <span>用户名：</span>
        <el-input v-model="addDeviceInfor.username" placeholder="请输入用户名"></el-input>
        <span>密码：</span>
        <el-input v-model="addDeviceInfor.password" placeholder="请输入密码"></el-input>
        <span>设备地址：</span>
        <el-input v-model="addDeviceInfor.address" placeholder="请输入设备地址"></el-input>
        <span>端口号：</span>
        <el-input v-model="addDeviceInfor.port" placeholder="请输入端口号"></el-input>
        <span slot="footer" class="dialog-footer">
    <el-button @click="createDialogVisible = false">取 消</el-button>
    <el-button type="primary" @click="createDevice">确 定</el-button>
  </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import {request, METHOD} from '@/utils/request'
import {DEVICE, DEVICE_DEL_ADD} from '@/services/api'

export default {
  name: 'proj_manage',
  i18n: require('./i18n'),
  data() {
    return {
      pageSize: 7,
      currentPage: 1,
      total: 100,
      tableData: [],
      addDeviceInfor: {
        'ip': '',
        'username': '',
        'password': '',
        'address': '',
        'port': '',
        'valid': true
      },
      addDevices: [],
      createDialogVisible: false,
      editDialogVisible: false,
      monitorDialogVisible: false
    }
  },
  activated() {
   this.getAllDevices()
  },
  mounted() {
    this.getAllDevices()
  },
  methods: {
    getAllDevices() {
      request(DEVICE, METHOD.POST, {
        project_name: ""
      }).then(res => {
        this.tableData = []
        for (let key in res.data.message) {
          this.tableData.push(
              {
                "address": res.data.message[key]["address"],
                "ip": key,
                "port": res.data.message[key]["port"],
                "username": res.data.message[key]["username"],
                "valid": res.data.message[key]["valid"] ? "有效" : "无效"
              }
          )
        }
        this.total = this.tableData.length
        console.log(this.tableData)
      })

    },
    handleDelete(index, row) {
      this.$confirm('此操作将删除该分布式设备, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
         request(DEVICE_DEL_ADD, METHOD.POST, {
          "cover": false,
          "add_devices": [],
          "rm_devices": [row.ip]
        }).then(res => {
          console.log(res)
            if (Object.getOwnPropertyNames(res.data.rm_error).length != 0) {
            this.$message({
              message: '删除失败',
              type: 'warning'
            });
          } else {
            this.createDialogVisible = false
            this.$message({
              message: '删除成功',
              type: 'success'
            });
            this.getAllDevices()
          }
         })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    handle_user_CurrentChange(val) {
      this.currentPage = val;
    },
    createDevice() {

      //请求服务器新建分布式设备
      if (this.addDeviceInfor.port == '' || this.addDeviceInfor.username == '' || this.addDeviceInfor.password == '' || this.addDeviceInfor.address == '' || this.addDeviceInfor.ip == '') {
        this.$message({
          message: '请输入完整信息',
          type: 'warning'
        });
      } else {
        let addDevices = [this.addDeviceInfor]
        request(DEVICE_DEL_ADD, METHOD.POST, {
          "cover": false,
          "add_devices": addDevices,
          "rm_devices": []
        }).then(res => {
          if (Object.getOwnPropertyNames(res.data.add_error).length != 0) {
            this.$message({
              message: '设备ip重复，创建失败',
              type: 'warning'
            });
          } else {
            this.createDialogVisible = false
            this.$message({
              message: '新建分布式设备成功',
              type: 'success'
            });
            this.getAllDevices()
          }
        })

      }
    },

  },

  computed: {
    ...mapState('setting', ['pageMinHeight']),
    desc() {
      return this.$t('description')
    }
  }
}
</script>

<style scoped lang="less">
@import "index";
</style>