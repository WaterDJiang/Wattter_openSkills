import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import {
  assertHttp,
  assertNoLocalImages,
  draftResult,
  formBody,
  getCookieHeader,
  parseJson,
  readPayloadFile,
  request,
  requireExecute,
  shortText,
} from '../_wtt_post/shared.js';

const HOME_URL = 'https://mp.weixin.qq.com/';
const CREATE_URL = (token) =>
  `https://mp.weixin.qq.com/cgi-bin/operate_appmsg?t=ajax-response&sub=create&type=77&token=${token}&lang=zh_CN`;

// 微信公众号公开错误码（来自现网 create 响应 base_resp.ret）。
const ERROR_MESSAGES = {
  '-6': '需要验证码，请到公众号后台手动处理后重试',
  '-8': '需要验证码，请到公众号后台手动处理后重试',
  '200003': '登录已失效，请重新登录公众号后台',
  '412': '正文含违规外链，请清理后重试',
  '62752': '正文含安全风险链接，请清理后重试',
  '64507': '正文含未授权外链，请清理后重试',
  '64702': '标题超过 64 个 Unicode 字符',
  '64703': '摘要超过 120 个字符',
  '64705': '正文超过长度限制',
  '10806': '正文可能含受限内容，请到公众号后台核对',
};

function formatError(ret) {
  const code = String(ret ?? '');
  return ERROR_MESSAGES[code] || `公众号草稿创建失败（错误码 ${code}）`;
}

cli({
  site: 'weixin',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建微信公众号图文草稿（Cookie 路径，无需 appid/secret）',
  domain: 'mp.weixin.qq.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '文章标题（≤64 Unicode 字符）' },
    { name: 'file', required: true, help: '已适配的微信公众号 UTF-8 HTML 文件（如 article.wechat.html）' },
    { name: 'summary', help: '文章摘要（≤120 字符，留空则由公众号自动生成）' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const content = await readPayloadFile(kwargs.file);
    assertNoLocalImages(content);
    const cookie = await getCookieHeader(page, [HOME_URL]);
    const headers = {
      Cookie: cookie,
      Origin: 'https://mp.weixin.qq.com',
      Referer: 'https://mp.weixin.qq.com/cgi-bin/appmsg',
    };

    // 解析后台首页 HTML：token 用于鉴权，nick_name/user_name 用于账号识别。
    const homeResponse = await request(HOME_URL, { headers });
    assertHttp(homeResponse.response, homeResponse.text, '检查公众号登录态');
    const home = homeResponse.text;
    const token = home.match(/t:\s*["']([^"']+)["']\s*\|\|/)?.[1];
    if (!token) throw new CliError('AUTH_REQUIRED', '未识别到公众号 token，请先登录 mp.weixin.qq.com');
    const account =
      home.match(/nick_name\s*=\s*["']([^"']+)["']/)?.[1] ||
      home.match(/user_name\s*=\s*["']([^"']+)["']/)?.[1] ||
      '公众号账号';

    const summary = String(kwargs.summary || '').trim();
    const createdResponse = await request(CREATE_URL(token), {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formBody({
        token,
        lang: 'zh_CN',
        f: 'json',
        ajax: '1',
        random: Math.random(),
        AppMsgId: '',
        count: '1',
        data_seq: '0',
        operate_from: 'Chrome',
        isnew: '0',
        // 单篇文章（index 0）。封面相关字段全部置空 —— 本 adapter 只写标题/正文/摘要，
        // 图片上传走 /cgi-bin/filetransfer + ticket，留待图片能力后续接入。
        title0: title,
        author0: '',
        writerid0: '0',
        fileid0: '',
        digest0: summary,
        auto_gen_digest0: summary ? '0' : '1',
        content0: content,
        sourceurl0: '',
        need_open_comment0: '1',
        only_fans_can_comment0: '0',
        cdn_url0: '',
        cdn_235_1_url0: '',
        cdn_1_1_url0: '',
        cdn_url_back0: '',
        crop_list0: '',
        music_id0: '',
        video_id0: '',
        voteid0: '',
        voteismlt0: '',
        supervoteid0: '',
        cardid0: '',
        cardquantity0: '',
        cardlimit0: '',
        vid_type0: '',
        show_cover_pic0: '0',
        shortvideofileid0: '',
        copyright_type0: '0',
        releasefirst0: '',
        platform0: '',
        reprint_permit_type0: '',
        allow_reprint0: '0',
        allow_reprint_modify0: '0',
        original_article_type0: '',
        ori_white_list0: '',
        free_content0: '',
        fee0: '0',
        ad_id0: '',
        guide_words0: '',
        is_share_copyright0: '0',
        share_copyright_url0: '',
        source_article_type0: '',
        reprint_recommend_title0: '',
        reprint_recommend_content0: '',
        share_page_type0: '0',
        share_imageinfo0: '{"list":[]}',
        share_video_id0: '',
        dot0: '{}',
        share_voice_id0: '',
        insert_ad_mode0: '',
        categories_list0: '[]',
      }),
    });
    assertHttp(createdResponse.response, createdResponse.text, '创建公众号草稿');
    const created = parseJson(createdResponse.text, '创建公众号草稿');
    const appMsgId = created?.appMsgId;
    const ret = created?.base_resp?.ret;
    if (!appMsgId) {
      throw new CliError('API_ERROR', formatError(ret) + ` ${shortText(createdResponse.text)}`);
    }
    return draftResult({
      platform: 'weixin',
      account,
      draftId: appMsgId,
      draftUrl: `https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=77&appmsgid=${appMsgId}&token=${token}&lang=zh_CN`,
      detail: '公众号草稿已创建（Cookie 路径）；仍需在后台回读标题/正文。未接入图片上传。',
    });
  },
});
