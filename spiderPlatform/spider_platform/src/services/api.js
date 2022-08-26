//跨域代理前缀
const API_PROXY_PREFIX = 'http://180.201.163.246:50001/'
const BASE_URL = process.env.NODE_ENV === 'production' ? process.env.VUE_APP_API_BASE_URL : API_PROXY_PREFIX
// const BASE_URL = process.env.VUE_APP_API_BASE_URL
module.exports = {
    LOGIN: `${BASE_URL}/login`,
    ROUTES: `${BASE_URL}/routes`,
    SPIDER_STATUS: `${BASE_URL}/update_cs_status`,
    SPIDER_DEL_ADD: `${BASE_URL}/update_cs`,
    DEVICE: `${BASE_URL}/get_device_info`,
    GET_PROJECTS_INFO: `${BASE_URL}/get_projects_info`,
    GET_DEVICE_INFO: `${BASE_URL}/get_device_info`,
    UPDATE_PROJECT_DEVICE: `${BASE_URL}/update_pro_device`,
    UPDATE_TIMING_JOB: `${BASE_URL}/update_timing_job`,
    RM_TIMING_JOB: `${BASE_URL}/rm_timing_job`,
    GET_ACCOUNT_INFO: `${BASE_URL}/get_account_info`,
    UPDATE_PRO_ACCOUNT: `${BASE_URL}/update_pro_account`,
    GET_HOT_SPIDER: `${BASE_URL}/get_all_hot_spider`,
    PAUSE_TIMING: `${BASE_URL}/pause_job`,
    START_TIMING: `${BASE_URL}/start_job`,
    ADD_KEYWORD: `${BASE_URL}/add_keyword`,
    GET_CUSTOM_KEYWORDS: `${BASE_URL}/get_custom_keywords`,
    ADD_HOT_SPIDER: `${BASE_URL}/add_hot_spider`,
    RM_HOT_SPIDER: `${BASE_URL}/rm_hot_spider`,
    DEVICE_DEL_ADD: `${BASE_URL}/update_sys_device`,
    ACCOUNT: `${BASE_URL}/get_account_info`,
    ACCOUNT_DEL_ADD: `${BASE_URL}/update_account`,
    DEL_ACCOUNT: `${BASE_URL}/rm_sys_account`,
    CONTENT_SPIDER: `${BASE_URL}/get_pro_content_spider`,
    GET_ALL_CONTENT_SPIDER: `${BASE_URL}/get_all_content_spider`,
    SPIDER_MONITOR: `${BASE_URL}/spider_monitor`,
    CREATE_PROJ: `${BASE_URL}/create_project`,
    DEL_PROJ: `${BASE_URL}/del_project`,
    DOWNLOAD_USER: `${BASE_URL}/download_user_data`,
    DOWNLOAD_NEWS: `${BASE_URL}/download_news_data`,
    SEC_MONITOR: `${BASE_URL}/sec_monitor`
}
