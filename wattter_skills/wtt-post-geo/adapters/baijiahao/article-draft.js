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

function parseJsonp(value) {
  const text = String(value || '').trim();
  const match = text.match(/^[\w$.]+\(([\s\S]*)\);?$/);
  return parseJson(match?.[1] || text, '创建百家号草稿');
}

cli({
  site: 'baijiahao',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建百家号图文草稿（无 CSDN 插件）',
  domain: 'baijiahao.baidu.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '文章标题' },
    { name: 'file', required: true, help: '已适配的 UTF-8 HTML 文件' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const content = await readPayloadFile(kwargs.file);
    assertNoLocalImages(content);
    const cookie = await getCookieHeader(page, ['https://baijiahao.baidu.com/']);
    const headers = { Cookie: cookie, Origin: 'https://baijiahao.baidu.com', Referer: 'https://baijiahao.baidu.com/' };

    const meResponse = await request(`https://baijiahao.baidu.com/builder/app/appinfo?_=${Date.now()}`, { headers });
    assertHttp(meResponse.response, meResponse.text, '检查百家号登录态');
    const me = parseJson(meResponse.text, '检查百家号登录态');
    const user = me?.data?.user;
    if (!user?.userid) throw new CliError('AUTH_REQUIRED', '未识别到百家号登录账号');

    const editorResponse = await request('https://baijiahao.baidu.com/builder/rc/edit', { headers });
    assertHttp(editorResponse.response, editorResponse.text, '获取百家号发布凭证');
    const token = editorResponse.text.match(/window\.__BJH__INIT__AUTH__\s*=\s*['"]([^'"]+)['"]/)?.[1];
    if (!token) throw new CliError('AUTH_REQUIRED', '百家号发布凭证缺失，请重新登录');

    const createdResponse = await request('https://baijiahao.baidu.com/pcui/article/save?callback=bjhdraft', {
      method: 'POST',
      headers: { ...headers, token, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formBody({
        type: 'news', title, content, feed_cat: '1', len: content.length,
        activity_list: JSON.stringify([{ id: 408, is_checked: 0 }]),
        source_reprinted_allow: '0', abstract_from: '1', isBeautify: 'false',
        usingImgFilter: 'false', first_exclusive_publish_v2: '3', subtitle: '',
        bjhtopic_id: '', bjhtopic_info: '',
      }),
    });
    assertHttp(createdResponse.response, createdResponse.text, '创建百家号草稿');
    const created = parseJsonp(createdResponse.text);
    const draftId = created?.ret?.article_id;
    if (!draftId || !(created.errmsg === 'success' || created.errno === 0)) {
      throw new CliError('API_ERROR', created.errmsg || `百家号草稿响应无效: ${shortText(createdResponse.text)}`);
    }
    return draftResult({
      platform: 'baijiahao',
      account: user.name || user.userid,
      draftId,
      draftUrl: `https://baijiahao.baidu.com/builder/rc/edit?type=news&article_id=${encodeURIComponent(draftId)}`,
    });
  },
});

