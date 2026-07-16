import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import {
  assertHttp,
  assertNoLocalImages,
  draftResult,
  getCookieHeader,
  parseCsv,
  parseJson,
  readPayloadFile,
  request,
  requireExecute,
} from '../_wtt_post/shared.js';

cli({
  site: 'juejin',
  name: 'article-draft',
  access: 'write',
  description: '使用浏览器登录态创建掘金文章草稿（无 CSDN 插件）',
  domain: 'api.juejin.cn',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [
    { name: 'title', required: true, help: '文章标题' },
    { name: 'file', required: true, help: '已适配的 UTF-8 Markdown 文件' },
    { name: 'summary', help: '文章摘要' },
    { name: 'category-id', default: '0', help: '掘金分类 ID' },
    { name: 'tag-ids', help: '逗号分隔的掘金标签 ID' },
    { name: 'cover-url', help: '已由掘金托管的封面 URL' },
    { name: 'execute', type: 'boolean', help: '确认创建草稿' },
  ],
  columns: ['status', 'write_state', 'provider', 'platform', 'account', 'draft_id', 'draft_url', 'detail'],
  func: async (page, kwargs) => {
    requireExecute(kwargs);
    const title = String(kwargs.title || '').trim();
    if (!title) throw new CliError('INVALID_INPUT', '--title is required');
    const markdown = await readPayloadFile(kwargs.file);
    assertNoLocalImages(markdown);
    const cookie = await getCookieHeader(page, ['https://juejin.cn/', 'https://api.juejin.cn/']);
    const headers = { Cookie: cookie, Origin: 'https://juejin.cn', Referer: 'https://juejin.cn/' };

    const meResponse = await request('https://api.juejin.cn/user_api/v1/user/get?not_self=0', { headers });
    assertHttp(meResponse.response, meResponse.text, '检查掘金登录态');
    const me = parseJson(meResponse.text, '检查掘金登录态');
    if (!me?.data?.user_id) throw new CliError('AUTH_REQUIRED', '未识别到掘金登录账号');

    const csrfResponse = await request('https://api.juejin.cn/user_api/v1/sys/token', {
      method: 'HEAD',
      headers: { ...headers, 'x-secsdk-csrf-request': '1', 'x-secsdk-csrf-version': '1.2.10' },
    });
    assertHttp(csrfResponse.response, csrfResponse.text, '获取掘金 CSRF token');
    const rawToken = csrfResponse.response.headers.get('x-ware-csrf-token') || '';
    const csrfToken = rawToken.includes(',') ? rawToken.split(',').at(-1).trim() : rawToken.trim();
    if (!csrfToken) throw new CliError('API_ERROR', '掘金 CSRF 响应缺少 token');

    const createdResponse = await request('https://api.juejin.cn/content_api/v1/article_draft/create', {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json', 'x-secsdk-csrf-token': csrfToken },
      body: JSON.stringify({
        brief_content: String(kwargs.summary || ''),
        category_id: String(kwargs['category-id'] || '0'),
        cover_image: String(kwargs['cover-url'] || ''),
        edit_type: 10,
        html_content: 'deprecated',
        link_url: '',
        mark_content: markdown,
        tag_ids: parseCsv(kwargs['tag-ids']),
        title,
      }),
    });
    assertHttp(createdResponse.response, createdResponse.text, '创建掘金草稿');
    const created = parseJson(createdResponse.text, '创建掘金草稿');
    if (created.err_no && created.err_no !== 0) throw new CliError('API_ERROR', created.err_msg || `掘金错误码 ${created.err_no}`);
    if (!created?.data?.id) throw new CliError('API_ERROR', '掘金草稿响应缺少 ID');
    return draftResult({
      platform: 'juejin',
      account: me.data.user_name || me.data.user_id,
      draftId: created.data.id,
      draftUrl: `https://juejin.cn/editor/drafts/${created.data.id}`,
    });
  },
});

