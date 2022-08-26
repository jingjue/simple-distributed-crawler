<template>
  <div class="new-page" :style="`min-height: ${pageMinHeight}px`">
    <div class="create">
      <el-button size="medium" @click="createDialogVisible=true"> + 新建用户</el-button>
    </div>
    <el-card style="margin: 20px">
       <div class="table">
      <el-table
          :data="tableData.slice((currentPage-1)*pageSize,currentPage*pageSize)"
          style="width: 100%">
        <el-table-column
            label="创建日期"
            sortable
            width="360">
          <template slot-scope="scope">
            <i class="el-icon-time"></i>
            <span style="margin-left: 10px">{{ scope.row.date }}</span>
          </template>
        </el-table-column>
        <el-table-column
            prop="name"
            label="用户名称"
            min-width="180">
        </el-table-column>
        <el-table-column
            prop="platform"
            label="平台"
            min-width="180">
        </el-table-column>
        <el-table-column
            prop="valid"
            label="是否有效"
            min-width="180">
        </el-table-column>
        <el-table-column
            label="操作"
            min-width="180">
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
          title="添加用户"
          :visible.sync="createDialogVisible"
          width="40%"
          center>
        <span>平台名称：</span>
        <el-input v-model="addAccountInfo.platform" placeholder="请输入平台名称"></el-input>
        <span>Cookie：</span>
        <el-input v-model="addAccountInfo.cookie" placeholder="请输入Cookie"></el-input>
        <span>用户名：</span>
        <el-input v-model="addAccountInfo.user" placeholder="请输入用户名"></el-input>
        <span>密码：</span>
        <el-input v-model="addAccountInfo.password" placeholder="请输入密码" show-password></el-input>
        <span slot="footer" class="dialog-footer">
    <el-button @click="createDialogVisible = false">取 消</el-button>
    <el-button type="primary" @click="createSpider">确 定</el-button>
  </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
import {request, METHOD} from '@/utils/request'
import {ACCOUNT, ACCOUNT_DEL_ADD, DEL_ACCOUNT} from '@/services/api'

export default {
  name: 'proj_manage',
  i18n: require('./i18n'),
  data() {
    return {
      addAccountInfo: {
        'platform': '',
        'user': '',
        'cookie': '',
        'password': '',
        'valid': true,
        'date': ''
      },
      pageSize: 7,
      currentPage: 1,
      total: 8,
      tableData: [],
      createDialogVisible: false,
      editDialogVisible: false,
      monitorDialogVisible: false
    }
  },
  mounted() {
    this.getAllAccount()
  },
  activated() {
    this.getAllAccount()
  },
  methods: {
    getAllAccount() {
      request(ACCOUNT, METHOD.POST, {
        project_name: "",
      }).then(res => {
        let data = []
        for (let platName in res.data.account) {
          for (let user in res.data.account[platName])
            data.push({
              id: res.data.account[platName][user]['id'],
              date: res.data.account[platName][user]['date'],
              name: res.data.account[platName][user]['user'],
              valid: res.data.account[platName][user]['valid'] === true ? "有效" : "失效",
              platform:res.data.account[platName][user]['platform']
            })
        }
        this.tableData = data
        this.total = this.tableData.length
        console.log(this.tableData)
      })
    },
    handleDelete(index, row) {
      console.log(index, row)
      this.$confirm('此操作将删除该用户, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        request(DEL_ACCOUNT, METHOD.POST, {
          'id': [row.id]
        }).then(res => {
          if (res.data.code === 200) {
            this.$message({
              type: 'success',
              message: '删除成功!'
            });
          } else {
            this.$message({
              type: 'warning',
              message: '删除失败'
            });
          }
          this.getAllAccount()
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
    createSpider() {
      if (this.addAccountInfo.platform === '' || this.addAccountInfo.user === '' || this.addAccountInfo.cookie === '' || this.addAccountInfo.password === '') {
        this.$message({
          message: '请输入完整信息',
          type: 'warning'
        });
      } else {
        this.addAccountInfo.date = this.getNowFormatTime()
        request(ACCOUNT_DEL_ADD, METHOD.POST, {
          account_infos: [this.addAccountInfo]
        }).then(res => {
          if (res.data.code === 200) {
            this.$message({
              message: '添加用户成功',
              type: 'success'
            });
          } else {
            this.$message({
              message: '添加用户失败',
              type: 'warning'
            });
          }
          this.getAllAccount()
          this.createDialogVisible = false
        })
      }
    },
    getNowFormatDay(nowDate) {
      var char = "-";
      if (nowDate == null) {
        nowDate = new Date();
      }
      var day = nowDate.getDate();
      var month = nowDate.getMonth() + 1;//注意月份需要+1
      var year = nowDate.getFullYear();
      //补全0，并拼接
      return year + char + this.completeDate(month) + char + this.completeDate(day);
    },
    getNowFormatTime() {
      var nowDate = new Date();
      var colon = ":";
      var h = nowDate.getHours();
      var m = nowDate.getMinutes();
      var s = nowDate.getSeconds();
      //补全0，并拼接
      return this.getNowFormatDay(nowDate) + " " + this.completeDate(h) + colon + this.completeDate(m) + colon + this.completeDate(s);
    },
    completeDate(value) {
      return value < 10 ? "0" + value : value;
    }
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