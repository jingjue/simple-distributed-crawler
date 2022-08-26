<template>
  <div class="new-page" :style="`min-height: ${pageMinHeight}px`">
    <el-tabs class="project_tab" v-model="activeName" @tab-click="spider_handleClick">
      <el-tab-pane label="任务管理" name="first">
        <div class="tab-title">
          <el-button @click="isCreateProjectBtnVisible = true">+ 创建任务</el-button>
          <el-button @click="downloadNewsDataVisible=true"> 导出舆情数据</el-button>
          <el-dialog
              title="提示"
              :visible.sync="downloadNewsDataVisible"
              width="30%"
              center>
            <p style="text-align: center">请选择需要导出的<b>爬虫任务</b></p>
            <el-select style="margin-left: 25%;width: 50%" v-model="downloadNewsDataSelect" placeholder="请选择">
              <el-option
                  v-for="item in allProject"
                  :key="item.name"
                  :label="item.name"
                  :value="item.name">
              </el-option>
            </el-select>
            <span slot="footer" class="dialog-footer">
            <el-button @click="downloadNewsDataVisible = false">取 消</el-button>
            <el-button v-loading="downloadNewsDataLoading"
                       @click="downloadNewsData">确 定</el-button>
          </span>
          </el-dialog>
          <el-button @click="downloadUserDataVisible=true" style="margin-left: 10px"> 导出用户数据</el-button>
          <el-dialog
              title="提示"
              :visible.sync="downloadUserDataVisible"
              width="30%"
              center>
            <span>此操作将导出当前所有<b>用户数据</b>，是否继续？</span>
            <span slot="footer" class="dialog-footer">
            <el-button @click="downloadUserDataVisible = false">取 消</el-button>
            <el-button v-loading="downloadUserDataLoading" type="primary" @click="downloadUserData">确 定</el-button>
          </span>
          </el-dialog>
        </div>
        <el-card class="box-card">
          <el-table :data="allProject" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="任务名称" min-width="100">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="描述信息" min-width="100">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.desc }}</span>
              </template>
            </el-table-column>
            <el-table-column label="创建日期" min-width="100">
              <template slot-scope="scope">
                <i class="el-icon-time"></i>
                <span style="margin-left: 10px">{{ scope.row.create_time }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="300">
              <template slot-scope="scope">
                <el-button size="mini" type="primary" @click="manageContentSpider(scope.$index, scope.row)"
                           plain>管理内容爬虫
                </el-button>
                <el-button size="mini" type="primary" @click="manageHotSpider(scope.$index, scope.row)"
                           plain>管理热点爬虫
                </el-button>
                <el-button size="mini" type="primary" @click="manageDistEquip(scope.$index, scope.row)"
                           plain>管理分布式设备
                </el-button>
                <el-button size="mini" type="primary" @click="managePlatAccount(scope.$index, scope.row)"
                           plain>管理平台账户
                </el-button>
                <el-button size="mini" type="primary" @click="monitorSecuritySituation(scope.$index, scope.row)"
                           plain>安全态势监测
                </el-button>
                <el-button size="mini" type="danger" @click="delProject(scope.$index, scope.row)"
                           plain>删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="提示" :visible.sync="isCreateProjectBtnVisible" width="30%">
          <div class="sub-title">请输入任务名称：</div>
          <el-input placeholder="任务名称" v-model="nameForProject" clearable></el-input>
          <div class="sub-title">请输入描述信息：</div>
          <el-input placeholder="描述信息" v-model="descForProject" clearable></el-input>
          <div class="sub-title">请输入作者名称：</div>
          <el-input placeholder="任务作者" v-model="authorForProject" clearable></el-input>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isCreateProjectBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="createNewProj">确 定</el-button>
          </span>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="爬虫管理" name="second" :disabled="true">
        <div class="tab-title">
          <el-button size="medium" @click="getContentSpider"> + 新建爬虫</el-button>
        </div>
        <el-card class="box-card">
          <el-table
              :data="spider_tableData"
              style="width: 100%">
            <el-table-column label="起始日期" sortable width="180">
              <template slot-scope="scope">
                <i class="el-icon-time"></i>
                <span style="margin-left: 10px">{{ scope.row.date }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="爬虫名称" min-width="180">
            </el-table-column>
            <el-table-column prop="device" label="所属设备" min-width="180">
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="180">
            </el-table-column>
            <el-table-column prop="tag" label="标签" min-width="100"
                             :filters="[{ text: '已启用', value: '已启用' }, { text: '已停用', value: '已停用' }]"
                             :filter-method="spider_filterTag" filter-placement="bottom-end">
              <template slot-scope="scope">
                <el-tag :type="scope.row.tag === '已启用' ? 'success' : 'danger'" disable-transitions>{{ scope.row.tag }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="180">
              <template slot-scope="scope">
                <el-button size="mini" @click="spider_edit(scope.$index, scope.row)">编辑
                </el-button>
                <el-button size="mini" type="danger" @click="spider_handleDelete(scope.$index, scope.row)">删除
                </el-button>
                <el-button size="mini" type="success" @click="monitorSpider(scope.$index, scope.row)">监控爬虫状态
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <div style="height:35px;width:100%" class="clspage">
          <el-pagination align='center' @current-change="spider_handle_user_CurrentChange" layout="prev, pager, next"
                         :page-size="spider_pageSize" :current-page="spider_currentPage"
                         :total="spider_total"></el-pagination>
        </div>
        <div class="dialog">
          <el-dialog
              title="新建爬虫"
              :visible.sync="spider_createDialogVisible"
              width="40%"
              center>
            <el-select style="margin-left: 35%" v-model="addSpider" multiple placeholder="请选择需要新建的爬虫">
              <el-option
                  v-for="item in addSpiderList"
                  :key="item"
                  :label="item"
                  :value="item">
              </el-option>
            </el-select>
            <span slot="footer" class="dialog-footer">
    <el-button @click="spider_createDialogVisible = false">取 消</el-button>
    <el-button type="primary" @click="createSpider">确 定 添 加</el-button>
  </span>
          </el-dialog>
          <el-dialog
              title="编辑爬虫"
              :visible.sync="spider_editDialogVisible"
              width="40%"
              center>
            <div style="text-align: center">
              <span style="margin-right:30px ">是否启用爬虫</span>
              <el-switch
                  v-model="spider_is_start"
                  active-color="#13ce66"
                  inactive-color="#ff4949">
              </el-switch>
            </div>

            <span slot="footer" class="dialog-footer">
    <el-button type="primary" @click="editSpider">确 定</el-button>
  </span>
          </el-dialog>
        </div>
      </el-tab-pane>
      <el-tab-pane label="热点爬虫" name="third" :disabled="true">
        <div class="tab-title">
          <el-button @click="isAddKeywordBtnVisible = true">+ 添加关键词</el-button>
          <el-button @click="isAddHotSpiderBtnVisible = true">+ 添加热点爬虫</el-button>
        </div>
        <el-card class="box-card">
          <el-table :data="allKeywordsForProject" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="关键词">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.keyword }}</span>
              </template>
            </el-table-column>
            <el-table-column label="标题">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="danger"
                           @click="deleteKeywordForProject(scope.$index, scope.row)" plain>删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-card class="box-card">
          <el-table :data="projectHotSpiders" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="平台">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.platform }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态">
              <template slot-scope="scope">
                <span style="margin-left: 10px" v-if="scope.row.status">已启用</span>
                <span style="margin-left: 10px" v-if="!scope.row.status">未启用</span>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="danger"
                           @click="removeHotSpider(scope.row.platform)" plain>取消
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="提示" :visible.sync="isAddHotSpiderBtnVisible" width="30%">
          <el-select v-model="newHotSpiderForProject" placeholder="请选择">
            <el-option
                v-for="hotSpider in allHotSpiders"
                :key="hotSpider"
                :label="hotSpider"
                :value="hotSpider">
            </el-option>
          </el-select>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isAddHotSpiderBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="addHotSpider">确 定</el-button>
          </span>
        </el-dialog>
        <el-dialog title="提示" :visible.sync="isAddKeywordBtnVisible" width="30%" :before-close="handleClose">
          <el-input placeholder="请输入标题" v-model="newTitleForProject" style="margin-bottom: 16px" clearable>
          </el-input>
          <el-input type="textarea" :rows="4" placeholder="请输入关键词，以换行符为分隔" v-model="newKeywordForProject"></el-input>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isAddKeywordBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="addHotSpiderKeyword">确 定</el-button>
          </span>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="定时任务" name="forth">
        <!--        <div class="tab-title">-->
        <!--          <el-button @click="isAddTimedTaskBtnVisible = true">+ 添加定时任务</el-button>-->
        <!--        </div>-->
        <el-card class="box-card">
          <el-table :data="allScheduleTask" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="名称">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="类型">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.trigger }}</span>
              </template>
            </el-table-column>
            <el-table-column label="任务">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.task }}</span>
              </template>
            </el-table-column>
            <el-table-column label="状态">
              <template slot-scope="scope">
                <span style="margin-left: 10px" v-if="scope.row.status === 1">运行中</span>
                <span style="margin-left: 10px" v-if="scope.row.status === 0">已暂停</span>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="success" @click="showUpdateTimingTaskDialog(scope.row)" plain>修改
                </el-button>
                <el-button size="mini" type="danger" v-if="scope.row.status === 1"
                           @click="pauseTimedTask(scope.row.name)" plain>暂停
                </el-button>
                <el-button size="mini" type="success" v-if="scope.row.status === 0"
                           @click="resumeTimedTask(scope.row.name)" plain>启用
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="提示" :visible.sync="isAddTimedTaskBtnVisible" width="30%">
          <div class="demo-input-suffix" v-if="timingTask.trigger === 'interval'">
            <div class="sub-title">名称</div>
            <el-input placeholder="请输入名称" v-model="timingTask.name" clearable></el-input>
            <div class="sub-title">天数</div>
            <el-input placeholder="请输入天数" v-model="timingTask.kwargs.day" type="number" clearable></el-input>
            <div class="sub-title">时数</div>
            <el-input placeholder="请输入时数" v-model="timingTask.kwargs.hour" type="number" clearable></el-input>
            <div class="sub-title">分数</div>
            <el-input placeholder="请输入分数" v-model="timingTask.kwargs.minute" type="number" clearable></el-input>
            <div class="sub-title">秒数</div>
            <el-input placeholder="请输入秒数" v-model="timingTask.kwargs.second" type="number" clearable></el-input>
          </div>
          <div class="demo-input-suffix block" v-if="timingTask.trigger === 'date'">
            <div class="sub-title">名称</div>
            <el-input placeholder="请输入名称" v-model="timingTask.name" clearable>
            </el-input>
            <div class="sub-title">日期</div>
            <el-date-picker v-model="timingTask.kwargs" type="datetime" placeholder="选择日期时间"></el-date-picker>
          </div>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isAddTimedTaskBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="updateTimingTask">确 定</el-button>
          </span>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="分布式设备" name="fifth" :disabled="true">
        <div class="tab-title">
          <el-button @click="isAddDistEquipBtnVisible = true">+ 添加分布式设备</el-button>
        </div>
        <el-card class="box-card">
          <el-table :data="distEquipsFroPoj.distEquips" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="IP地址">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.ip }}</span>
              </template>
            </el-table-column>
            <el-table-column label="端口号">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.port }}</span>
              </template>
            </el-table-column>
            <el-table-column label="用户名">
              <template slot-scope="scope">
                <i class="el-icon-time"></i>
                <span style="margin-left: 10px">{{ scope.row.username }}</span>
              </template>
            </el-table-column>
            <el-table-column label="设备地址">
              <template slot-scope="scope">
                <i class="el-icon-time"></i>
                <span style="margin-left: 10px">{{ scope.row.address }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="danger"
                           @click="removeProjectDevice(scope.row.ip, scope.row.port)" plain>删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="提示" :visible.sync="isAddDistEquipBtnVisible" width="30%">
          <el-select v-model="newDistEquipIp" placeholder="请选择">
            <el-option
                v-for="distEquip in allDistEquip"
                :key="distEquip.ip"
                :label="distEquip.ip + ':' + distEquip.port"
                :value="distEquip.ip + ':' + distEquip.port">
            </el-option>
          </el-select>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isAddDistEquipBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="addProjectDevice()">确 定</el-button>
          </span>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="平台账户" name="sixth" :disabled="true">
        <div class="tab-title">
          <el-button @click="isAddPlatformAccountsBtnVisible = true">+ 添加平台账户</el-button>
        </div>
        <el-card class="box-card">
          <el-table :data="projectAccounts" style="width: 100%">
            <el-table-column type="index"></el-table-column>
            <el-table-column label="平台">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.platform }}</span>
              </template>
            </el-table-column>
            <el-table-column label="名称">
              <template slot-scope="scope">
                <span style="margin-left: 10px">{{ scope.row.user }}</span>
              </template>
            </el-table-column>
            <el-table-column label="添加日期">
              <template slot-scope="scope">
                <i class="el-icon-time"></i>
                <span style="margin-left: 10px">{{ scope.row.date }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template slot-scope="scope">
                <el-button size="mini" type="danger"
                           @click="deleteProjectAccount(scope.row)"
                           plain>删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
        <el-dialog title="提示" :visible.sync="isAddPlatformAccountsBtnVisible" width="30%">
          <el-select v-model="newProjectAccount" placeholder="请选择">
            <el-option
                v-for="item in allAccounts"
                :key="item.platform + ': ' + item.user"
                :label="item.platform + ': ' + item.user"
                :value="item.platform + ': ' + item.user">
            </el-option>
          </el-select>
          <span slot="footer" class="dialog-footer">
            <el-button @click="isAddPlatformAccountsBtnVisible = false">取 消</el-button>
            <el-button type="primary" @click="addProjectAccount">确 定</el-button>
          </span>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="爬虫状态" name="seventh" :disabled="true">
        <el-card class="box-card">
          <el-row>
            <el-col :span="8">
              <div class="grid-content bg-purple">
                <el-card class="box-card2">
                  <h2>开始时间</h2>
                  <h3>{{ spiderStatus.startTime }}</h3>
                </el-card>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="grid-content bg-purple-light">
                <el-card class="box-card2">
                  <h2>停止时间</h2>
                  <h3>{{ spiderStatus.endTime }}</h3>
                </el-card>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="grid-content bg-purple">
                <el-card class="box-card2">
                  <h2>终止原因</h2>
                  <h3>{{ spiderStatus.closedReason }}</h3>
                </el-card>
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="12">
              <div class="grid-content bg-purple">
                <el-card class="box-card2">
                  <div id="dataVolume" style="width: 707px; height: 300px"></div>
                </el-card>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="grid-content bg-purple-light">
                <el-card class="box-card2">
                  <div id="reqRespVolume" style="width: 707px; height: 300px"></div>
                </el-card>
              </div>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="12">
              <div class="grid-content bg-purple">
                <el-card class="box-card2">
                  <div id="queueVolume" style="width: 707px; height: 300px"></div>
                </el-card>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="grid-content bg-purple-light">
                <el-card class="box-card2">
                  <div id="statusRespVolume" style="width: 707px; height: 300px"></div>
                </el-card>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="安全态势监测" name="eighth" :disabled="true">
        <div class="new-page" style="min-height: 700px">
          <el-row>
            <el-col :span="12">
              <el-card class="box-card">
                <div id="emotion" class="chart" style="width: 765px; height: 658px;"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="box-card">
                <div id="keywords" class="chart" style="width: 765px; height: 658px;"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
<style lang="less" src="./index.less"></style>

<script>
import {mapState} from 'vuex';
import {METHOD, request} from '@/utils/request';
import {
  ADD_HOT_SPIDER,
  ADD_KEYWORD,
  CONTENT_SPIDER,
  GET_ACCOUNT_INFO,
  GET_ALL_CONTENT_SPIDER,
  GET_CUSTOM_KEYWORDS,
  GET_DEVICE_INFO,
  GET_HOT_SPIDER,
  GET_PROJECTS_INFO,
  PAUSE_TIMING,
  RM_HOT_SPIDER,
  SPIDER_DEL_ADD,
  SPIDER_STATUS,
  START_TIMING,
  UPDATE_PRO_ACCOUNT,
  UPDATE_PROJECT_DEVICE,
  UPDATE_TIMING_JOB,
  SPIDER_MONITOR,
  CREATE_PROJ,
  DEL_PROJ,
  DOWNLOAD_USER,
  DOWNLOAD_NEWS,
  SEC_MONITOR
} from '@/services/api';
import * as echarts from "echarts";


// import axios from "axios";

export default {
  name: 'proj_manage',
  i18n: require('./i18n'),
  data() {
    return {
      downloadNewsDataSelect: "",
      downloadNewsDataLoading: false,
      downloadUserDataLoading: false,
      downloadUserDataVisible: false,
      downloadNewsDataVisible: false,
      nameForProject: '',
      descForProject: "",
      authorForProject: '',
      addSpider: [],
      addSpiderList: [],
      nowProject: '',
      edit_spider_index: null,
      edit_spider_row: null,
      spider_is_start: true,
      activeName: 'first',
      spider_pageSize: 7,
      spider_currentPage: 1,
      spider_total: 4,
      spider_tableData: [],
      spider_createDialogVisible: false,
      spider_editDialogVisible: false,
      allHotSpiders: [],
      allKeywordsForProject: [],
      newHotSpiderForProject: "",
      projectHotSpiders: [],
      isAddKeywordBtnVisible: false,
      isAddHotSpiderBtnVisible: false,
      newTitleForProject: "",
      newKeywordForProject: "",

      isAddTimedTaskBtnVisible: false,
      isAddDistEquipBtnVisible: false,
      isCreateProjectBtnVisible: false,
      isAddPlatformAccountsBtnVisible: false,

      allProject: [],
      currentProject: null,

      newDistEquipIp: "",
      allDistEquip: [],
      distEquipsFroPoj: {projectName: "", distEquips: []},

      timingTask: {},
      allScheduleTask: [],
      projectAccounts: [],
      allAccounts: [],

      newProjectAccount: "",
      spiderStatus: {
        startTime: "",
        endTime: "",
        closedReason: ""
      },

      emotionDom: null,
      emotionChart: null,
      emotionOption: null,
      keywordsDom: null,
      keywordsChart: null,
      keywordsOption: null
    }
  },
  methods: {
    downloadNewsData() {
      this.downloadNewsDataLoading = true
      request(DOWNLOAD_NEWS, METHOD.POST, {
        project_name: this.downloadNewsDataSelect
      }).then(res => {
        const data = res.data
        // let url = window.URL.createObjectURL(data)
        let binaryData = [];
        binaryData.push(data);
        let url = window.URL.createObjectURL(new Blob(binaryData));
        var a = document.createElement('a')
        document.body.appendChild(a)
        a.href = url
        a.download = 'news_rawdata.csv'
        a.click()
        window.URL.revokeObjectURL(url)
        this.downloadNewsDataLoading = false
        this.downloadNewsDataVisible = false
      })
    },
    downloadUserData() {
      this.downloadUserDataLoading = true
      request(DOWNLOAD_USER, METHOD.GET).then(res => {
        const data = res.data
        // let url = window.URL.createObjectURL(data)
        let binaryData = [];
        binaryData.push(data);
        let url = window.URL.createObjectURL(new Blob(binaryData));
        var a = document.createElement('a')
        document.body.appendChild(a)
        a.href = url
        a.download = 'users_rawdata.csv'
        a.click()
        window.URL.revokeObjectURL(url)
        this.downloadUserDataLoading = false
        this.downloadUserDataVisible = false
      })
    },
    delProject(index, row) {
      this.$confirm('此操作将删除该任务, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        request(DEL_PROJ, METHOD.POST, {
          project_name: row.name
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
          this.queryProjects()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    completeDate(value) {
      return value < 10 ? "0" + value : value;
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
    getLastFormatDay(nowDate) {
      var char = "-";
      if (nowDate == null) {
        nowDate = new Date();
      }
      var day = nowDate.getDate();
      var month = nowDate.getMonth() + 1;//注意月份需要+1
      var year = nowDate.getFullYear();
      //补全0，并拼接
      return year - 1 + char + this.completeDate(month) + char + this.completeDate(day);
    },
    getLastFormatTime() {
      var nowDate = new Date();
      var colon = ":";
      var h = nowDate.getHours();
      var m = nowDate.getMinutes();
      var s = nowDate.getSeconds();
      //补全0，并拼接
      return this.getLastFormatDay(nowDate) + " " + this.completeDate(h) + colon + this.completeDate(m) + colon + this.completeDate(s);
    },
    createNewProj() {
      let that = this
      request(CREATE_PROJ, METHOD.POST, {
        param: {
          "author": that.authorForProject,
          "create_time": that.getNowFormatTime(),
          "name": that.nameForProject,
          "desc": that.descForProject,
          "spider_manager": {
            "project_name": that.nameForProject,
            "spiders": {}
          },
          "hot_spider_config": {},
          "devices_manager": {
            "127.0.0.1": true
          },
          "crawl_time": {
            "start": that.getLastFormatTime(),
            "end": that.getNowFormatTime()
          }
        }
      }).then(res => {
        if (res.data.code === 200) {
          this.$message({
            message: '创建任务成功',
            type: 'success'
          });
          this.queryProjects()
        } else {
          this.$message({
            message: '创建任务失败',
            type: 'warning'
          });
        }
      })

      this.isCreateProjectBtnVisible = false;
    },
    getContentSpider() {
      this.spider_createDialogVisible = true
      let that = this
      that.addSpider = []
      request(GET_ALL_CONTENT_SPIDER, METHOD.GET, {}).then(res => {
        let nowSpider = []
        for (let i in this.spider_tableData) {
          nowSpider.push(this.spider_tableData[i]['name'])
        }
        let spiderOptions = res.data.content_spiders.filter(v => !nowSpider.includes(v))
        that.addSpiderList = spiderOptions
      })
    },
    getHotSpiders() {
      const that = this;
      request(GET_HOT_SPIDER, METHOD.GET).then(res => {
        if (res.data.code === 200) {
          that.allHotSpiders = [];
          that.allHotSpiders = res.data.hot_spiders;
        }
      });
    },
    getHotSpidersForProject(projectName) {
      const that = this;
      request(GET_PROJECTS_INFO, METHOD.POST, {
        project_name: projectName
      }).then(res => {
        if (res.data.code === 200) {
          let allSpiders = res.data.message.hot_spider_config;
          that.projectHotSpiders = [];
          for (let key in allSpiders) {
            that.projectHotSpiders.push({"platform": key, "status": allSpiders[key]});
          }
        }
      });
    },
    getAllKeywordsForProject() {
      const that = this;
      let project_name = that.currentProject.name;
      request(GET_CUSTOM_KEYWORDS, METHOD.POST, {
        "project_name": project_name
      }).then(res => {
        if (res.data.code === 200) {
          that.allKeywordsForProject = [];
          that.allKeywordsForProject = res.data.message;
        }
      });
    },
    addHotSpider() {
      const that = this;
      let projectName = that.currentProject.name;
      request(ADD_HOT_SPIDER, METHOD.POST, {
        "project_name": projectName,
        "add_spider": [that.newHotSpiderForProject]
      }).then(res => {
        if (res.data.code === 200) {
          that.getHotSpidersForProject(that.currentProject.name);
          that.isAddHotSpiderBtnVisible = false;
        }
      });
    },
    removeHotSpider(hotSpider) {
      const that = this;
      let projectName = that.currentProject.name;
      request(RM_HOT_SPIDER, METHOD.POST, {
        "project_name": projectName,
        "rm_spider": [hotSpider]
      }).then(res => {
        if (res.data.code === 200) {
          that.getHotSpidersForProject(that.currentProject.name);
          that.isAddHotSpiderBtnVisible = false;
        }
      });
    },
    addHotSpiderKeyword() {
      const that = this;
      let project_name = that.currentProject.name;
      let newTitle = that.newTitleForProject;
      let allKeywords = that.newKeywordForProject.split("\n");
      request(ADD_KEYWORD, METHOD.POST, {
        "project_name": project_name,
        "add_keywords": {"title": newTitle, "keywords": allKeywords},
        "rm_keywords": {}
      }).then(function () {
        that.getAllKeywordsForProject();
        that.isAddKeywordBtnVisible = false;
      });
    },
    deleteKeywordForProject(index, row) {
      const that = this;
      let project_name = that.currentProject.name;
      let keyword = {};
      keyword["title"] = row.title;
      keyword["keywords"] = [row.keyword];
      request(ADD_KEYWORD, METHOD.POST, {
        "project_name": project_name,
        "add_keywords": {},
        "rm_keywords": keyword
      }).then(function () {
        that.getAllKeywordsForProject();
        that.isAddKeywordBtnVisible = false;

      });
    },
    queryProjects() {
      const that = this;
      request(GET_PROJECTS_INFO, METHOD.POST, {
        project_name: ""
      }).then(res => {
        if (res.data.code === 200) {
          that.allProject = res.data.message.projects;
        }
      });
    },
    manageContentSpider(index, row) {
      const that = this;
      that.activeName = "second";
      this.getAllContentSpider(row.name)
      this.nowProject = row.name
    },
    async getAllContentSpider(projectName) {
      await request(CONTENT_SPIDER, METHOD.POST, {
        project_name: projectName,
      }).then(res => {
        let newData = []
        for (let device in res.data.content) {
          for (let spider in res.data.content[device]) {
            newData.push({
              date: res.data.content[device][spider]['start_time'],
              name: spider,
              n_name: spider,
              tag: res.data.content[device][spider]['label'] === true ? '已启用' : '已禁用',
              device: device,
              status: res.data.content[device][spider]['status']
            })
          }
        }
        this.spider_tableData = newData
      })

    },
    manageHotSpider(index) {
      const that = this;
      that.activeName = "third";
      that.currentProject = that.allProject[index];
      let allSpiders = that.currentProject.hot_spider_config;
      that.projectHotSpiders = [];
      for (let key in allSpiders) {
        that.projectHotSpiders.push({"platform": key, "status": allSpiders[key]});
      }
      that.getHotSpiders();
      that.getAllKeywordsForProject();
    },
    manageDistEquip(index) {
      const that = this;
      that.activeName = "fifth";
      that.currentProject = that.allProject[index];
      request(GET_DEVICE_INFO, METHOD.POST, {
        project_name: that.currentProject.name
      }).then(res => {
        if (res.data.code === 200) {
          that.distEquipsFroPoj.distEquips = [];
          for (let key in res.data.message) {
            that.distEquipsFroPoj.distEquips.push(res.data.message[key]);
          }
        }
      });
      request(GET_DEVICE_INFO, METHOD.POST, {
        project_name: ""
      }).then(res => {
        if (res.data.code === 200) {
          let distEquips = res.data.message;
          that.allDistEquip = [];
          for (let key in distEquips) {
            that.allDistEquip.push(distEquips[key]);
          }
        }
      });
    },
    managePlatAccount(index) {
      const that = this;
      that.activeName = "sixth";
      that.currentProject = that.allProject[index];
      that.queryProjectAccount();
    },
    monitorSecuritySituation(index) {
      const that = this;
      that.activeName = "eighth";
      that.currentProject = that.allProject[index];

      this.emotionDom = document.getElementById('emotion');
      this.emotionChart = echarts.init(this.emotionDom);
      this.keywordsDom = document.getElementById('keywords');
      this.keywordsChart = echarts.init(this.keywordsDom);

      this.emotionOption = {
        title: {
          text: '情感走势'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: []
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: true,
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: []
      };
      this.emotionOption && this.emotionChart.setOption(this.emotionOption);

      this.keywordsOption = {
        title: {
          text: '关键词走势'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: []
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {}
          }
        },
        xAxis: {
          type: 'category',
          boundaryGap: true,
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: []
      };
      this.keywordsOption && this.keywordsChart.setOption(this.keywordsOption);

      request(SEC_MONITOR, METHOD.POST, {
        "project_name": that.currentProject.name,
        "mode": "day"
      }).then(function (data) {
        console.log(data.data.data);
        let emotionData = [];
        let emotionLegend = [];
        let emotions = data.data.data["emotion"];
        for (let key in emotions) {
          let emo;
          if ("neg" === key) {
            emo = "消极";
          } else if ("pos" === key) {
            emo = "积极";
          }
          emotionLegend.push(emo);
          emotionData.push(
              {
                name: emo,
                type: 'line',
                stack: emo,
                smooth: true,
                data: emotions[key]
              },
          );
        }
        that.emotionOption.legend.data = emotionLegend;
        that.emotionOption.series = emotionData;

        let keywordData = [];
        let keywordLegend = [];
        let keywords = data.data.data["keywords"];
        for (let key in keywords) {
          keywordLegend.push(key);
          keywordData.push(
              {
                name: key,
                type: 'line',
                stack: key,
                smooth: true,
                data: keywords[key]
              },
          );
        }
        that.keywordsOption.legend.data = keywordLegend;
        that.keywordsOption.series = keywordData;

        that.emotionOption.xAxis.data = data.data.data["x"];
        that.keywordsOption.xAxis.data = data.data.data["x"];

        that.emotionOption && that.emotionChart.setOption(that.emotionOption);
        that.keywordsOption && that.keywordsChart.setOption(that.keywordsOption);
      });
    },
    reloadProjectDevice() {
      const that = this;
      request(GET_DEVICE_INFO, METHOD.POST, {
        project_name: that.currentProject.name
      }).then(res => {
        if (res.data.code === 200) {
          that.distEquipsFroPoj.distEquips = [];
          for (let key in res.data.message) {
            that.distEquipsFroPoj.distEquips.push(res.data.message[key]);
          }
        }
      });
    },
    addProjectDevice() {
      const that = this;
      request(UPDATE_PROJECT_DEVICE, METHOD.POST, {
        "project_name": that.currentProject.name,
        "add_ip": [that.newDistEquipIp],
        "rm_ip": []
      }).then(res => {
        if (res.data.code === 200) {
          that.reloadProjectDevice();
          that.isAddDistEquipBtnVisible = false;
        }
      });
    },
    removeProjectDevice(distEquipIpToRemove, distEquipPortToRemove) {
      const that = this;
      let ip2port = distEquipIpToRemove + ":" + distEquipPortToRemove;
      request(UPDATE_PROJECT_DEVICE, METHOD.POST, {
        "project_name": that.currentProject.name,
        "add_ip": [],
        "rm_ip": [ip2port]
      }).then(res => {
        if (res.data.code === 200) {
          that.reloadProjectDevice();
        }
      });
    },
    updateTimingTask() {
      const that = this;
      let a_name = that.timingTask.name;

      let a_obj = {};
      a_obj["timing_job"] = {};
      if (that.timingTask.trigger === "interval") {
        that.timingTask.kwargs.day = Number(that.timingTask.kwargs.day);
        that.timingTask.kwargs.hour = Number(that.timingTask.kwargs.hour);
        that.timingTask.kwargs.minute = Number(that.timingTask.kwargs.minute);
        that.timingTask.kwargs.second = Number(that.timingTask.kwargs.second);
      }

      a_obj["timing_job"][a_name] = that.timingTask;

      request(UPDATE_TIMING_JOB, METHOD.POST, a_obj).then(function () {
        that.queryAllScheduleTask();
        that.isAddTimedTaskBtnVisible = false;
      });
    },
    spider_filterTag(value, row) {
      return row.tag === value;
    },
    spider_handleClick(tab) {
      const that = this;
      if (tab.index === "3") {
        that.queryAllScheduleTask();
      } else if (tab.index === "5") {
        that.queryProjectAccount();
      } else if (tab.index === "2") {
        that.getHotSpiders();
        that.activeName = "third";
      }
    },
    queryAllScheduleTask() {
      const that = this;
      request(GET_PROJECTS_INFO, METHOD.POST, {
        project_name: ""
      }).then(res => {
        if (res.data.code === 200) {
          let jobManager = res.data.message.job_manager;
          that.allScheduleTask = []
          for (let key in jobManager) {
            that.allScheduleTask.push(jobManager[key]);
          }
        }
      });
    },
    spider_handleDelete(index, row) {
      const that = this;
      this.$confirm('此操作将删除该爬虫, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }).then(() => {
        request(SPIDER_DEL_ADD, METHOD.POST, {
          "project_name": that.nowProject,
          "add_spiders": [],
          "rm_spiders": row.n_name
        }).then(res => {
          if (res.data.code == 300) {
            this.$message({
              message: '不存在该爬虫任务',
              type: 'warning'
            });
          } else {
            this.$message({
              message: '删除爬虫成功',
              type: 'success'
            });
            this.spider_tableData.splice(index, 1)
          }
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });
    },
    spider_handle_user_CurrentChange(val) {
      this.currentPage = val;
    },
    createSpider() {
      //在这里请求服务器获取到可以添加的爬虫，并且对比此任务已有的爬虫更新options
      //请求服务器新建爬虫
      if (this.addSpider.length == 0) {
        this.$message({
          message: '未选择爬虫',
          type: 'warning'
        });
      } else {
        request(SPIDER_DEL_ADD, METHOD.POST, {
          "project_name": this.nowProject,
          "add_spiders": this.addSpider,
          "rm_spiders": ""
        }).then(res => {
          if (res.data.code == 300) {
            this.$message({
              message: '不存在该爬虫任务',
              type: 'warning'
            });
          } else {
            this.$message({
              message: '添加成功',
              type: 'success'
            });
            this.getAllContentSpider(this.nowProject)
          }
        })
      }
      this.spider_createDialogVisible = false
    },
    spider_edit(index, row) {
      this.spider_editDialogVisible = true
      this.spider_is_start = row.tag == '已启用' ? true : false
      this.edit_spider_index = index
      this.edit_spider_row = row
      // 根据原始数据更新按钮
    },
    editSpider() {
      let status = this.edit_spider_row.tag == '已启用' ? false : true
      let name = this.edit_spider_row.n_name
      let spider_status = {}
      spider_status[name] = status
      request(SPIDER_STATUS, METHOD.POST, {
        project_name: this.nowProject,
        spider_status: spider_status
      }).then(res => {
        if (res.data.code == 300) {
          this.$message({
            message: '不存在该爬虫任务',
            type: 'warning'
          });
        } else {
          this.$message({
            message: '编辑爬虫成功',
            type: 'success'
          });
          this.spider_tableData[this.edit_spider_index].tag = this.spider_is_start ? "已启用" : "已停用"
        }
      })
      this.spider_editDialogVisible = false
    },
    monitorSpider(index, row) {
      console.log(index, row);
      const that = this;
      that.activeName = "seventh";
      request(SPIDER_MONITOR, METHOD.POST, {
        "project_name": that.nowProject,
        "platform": row.n_name
      }).then(function (e) {
        if (e.data.code === 200)
          that.parseSpiderStatus(e.data.data);
      });
    },
    parseSpiderStatus(originData) {
      this.spiderStatus.startTime = originData.start_time;
      this.spiderStatus.endTime = originData.end_time;
      this.spiderStatus.closedReason = originData.closed_reason;

      let dataVolumeChartDom = document.getElementById('dataVolume');
      let dataVolumeChart = echarts.init(dataVolumeChartDom);
      let dataVolumeChartOption = {
        title: {
          text: "数据量"
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['数据量']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: originData.x
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: '数据量',
          type: 'line',
          stack: 'Total',
          data: originData["数据量"],
          smooth: true
        }]
      };
      dataVolumeChartOption && dataVolumeChart.setOption(dataVolumeChartOption);

      let reqRespVolumeChartDom = document.getElementById('reqRespVolume');
      let reqRespVolumeChart = echarts.init(reqRespVolumeChartDom);
      let reqRespVolumeChartOption = {
        title: {
          text: "请求和响应量"
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['请求量', '响应量']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: originData.x
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '请求量',
            type: 'line',
            stack: 'Total',
            data: originData["请求量"],
            smooth: true
          },
          {
            name: '响应量',
            type: 'line',
            stack: 'Total',
            data: originData["响应量"],
            smooth: true
          }
        ]
      };
      reqRespVolumeChartOption && reqRespVolumeChart.setOption(reqRespVolumeChartOption);

      let queueVolumeChartDom = document.getElementById('queueVolume');
      let queueVolumeChart = echarts.init(queueVolumeChartDom);
      let queueVolumeChartOption = {
        title: {
          text: "队列量"
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['待请求数量', '已抓取数量']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: originData.x
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '待请求数量',
            type: 'line',
            stack: 'Total',
            data: originData["待请求数量"],
            smooth: true
          },
          {
            name: '已抓取数量',
            type: 'line',
            stack: 'Total',
            data: originData["已抓取数量"],
            smooth: true
          }
        ]
      };
      queueVolumeChartOption && queueVolumeChart.setOption(queueVolumeChartOption);

      let statusRespVolumeChartDom = document.getElementById('statusRespVolume');
      let statusRespVolumeChart = echarts.init(statusRespVolumeChartDom);
      let statusRespVolumeChartOption = {
        title: {
          text: "状态码响应数"
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['200', '301', '404']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: originData.x
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '200',
            type: 'line',
            stack: 'Total',
            data: originData["200"],
            smooth: true
          },
          {
            name: '301',
            type: 'line',
            stack: 'Total',
            data: originData["301"],
            smooth: true
          },
          {
            name: '404',
            type: 'line',
            stack: 'Total',
            data: originData["404"],
            smooth: true
          }
        ]
      };
      statusRespVolumeChartOption && statusRespVolumeChart.setOption(statusRespVolumeChartOption);
    },
    showUpdateTimingTaskDialog(job) {
      this.timingTask = job;
      this.isAddTimedTaskBtnVisible = true;
    },
    resumeTimedTask(job_name) {
      const that = this;
      request(START_TIMING, METHOD.POST, {
        "timing_job_name": job_name
      }).then(function () {
        that.queryAllScheduleTask();
        that.isAddTimedTaskBtnVisible = false;
      });
    },
    pauseTimedTask(job_name) {
      const that = this;
      request(PAUSE_TIMING, METHOD.POST, {
        "timing_job_name": job_name
      }).then(function () {
        that.queryAllScheduleTask();
        that.isAddTimedTaskBtnVisible = false;
      });
    },
    addProjectAccount() {
      const that = this;
      let pro_name = that.currentProject.name;
      let pltAccount = that.newProjectAccount.split(": ");
      let plt = pltAccount[0];
      let account = pltAccount[1];
      let reqObj = {
        "project_name": pro_name,
        "update_acc": {}
      };
      reqObj.update_acc[plt] = {
        "add": [account],
        "rm": []
      };
      request(UPDATE_PRO_ACCOUNT, METHOD.POST, reqObj).then(function () {
        that.queryProjectAccount();
        that.isAddPlatformAccountsBtnVisible = false;
      });
    },
    deleteProjectAccount(row) {
      const that = this;
      let pro_name = that.currentProject.name;
      let account = row.user;
      let plt = row.platform;
      let reqObj = {
        "project_name": pro_name,
        "update_acc": {}
      };
      reqObj.update_acc[plt] = {
        "add": [],
        "rm": [account]
      };
      request(UPDATE_PRO_ACCOUNT, METHOD.POST, reqObj).then(function () {
        that.queryProjectAccount();
        that.isAddPlatformAccountsBtnVisible = false;
      });
    },
    handleClose() {
      this.isAddDistEquipBtnVisible = false;
    },
    queryProjectAccount() {
      const that = this;
      let pro_name = that.currentProject.name;
      request(GET_ACCOUNT_INFO, METHOD.POST, {
        project_name: pro_name
      }).then(res => {
        if (res.data.code === 200) {
          that.projectAccounts = [];
          let accounts = res.data.account;
          for (let plt in accounts) {
            let pltAccounts = accounts[plt];
            for (let key in pltAccounts) {
              that.projectAccounts.push(pltAccounts[key]);
            }
          }
        }
      });
      request(GET_ACCOUNT_INFO, METHOD.POST, {
        project_name: ""
      }).then(res => {
        if (res.data.code === 200) {
          that.allAccounts = [];
          let accounts = res.data.account;
          for (let plt in accounts) {
            let pltAccounts = accounts[plt];
            for (let key in pltAccounts) {
              that.allAccounts.push(pltAccounts[key]);
            }
          }
        }
      });
    }
  },
  mounted() {
    this.queryProjects();
  },
  computed: {
    ...mapState('setting', ['pageMinHeight']),
    desc() {
      return this.$t('description')
    }
  }
}
</script>

<style lang="less">
@import "index";

.box-card {
  margin: 20px;
}

.tab-title {
  display: flex;
  flex-flow: row;
  padding: 20px 20px 0;
}

.box-card2 {
  margin: 8px;
}

</style>
