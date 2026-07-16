import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import { accountResult, assertHttp, getCookieHeader, parseJson, request } from '../_wtt_post/shared.js';

cli({
  site: 'juejin',
  name: 'draft-account',
  description: '检查掘金草稿 adapter 的当前登录账号',
  access: 'read',
  domain: 'api.juejin.cn',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [],
  columns: ['status', 'platform', 'account', 'account_id'],
  func: async (page) => {
    const cookie = await getCookieHeader(page, ['https://juejin.cn/', 'https://api.juejin.cn/']);
    const result = await request('https://api.juejin.cn/user_api/v1/user/get?not_self=0', {
      headers: { Cookie: cookie, Origin: 'https://juejin.cn', Referer: 'https://juejin.cn/' },
    });
    assertHttp(result.response, result.text, '检查掘金登录账号');
    const data = parseJson(result.text, '检查掘金登录账号');
    if (!data?.data?.user_id) throw new CliError('AUTH_REQUIRED', '未识别到掘金登录账号');
    return accountResult({ platform: 'juejin', account: data.data.user_name, accountId: data.data.user_id });
  },
});
