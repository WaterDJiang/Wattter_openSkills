import { CliError } from '@jackwener/opencli/errors';
import { cli, Strategy } from '@jackwener/opencli/registry';
import { accountResult, assertHttp, getCookieHeader, parseJson, request } from '../_wtt_post/shared.js';

cli({
  site: 'baijiahao',
  name: 'draft-account',
  description: '检查百家号草稿 adapter 的当前登录账号',
  access: 'read',
  domain: 'baijiahao.baidu.com',
  strategy: Strategy.COOKIE,
  browser: true,
  navigateBefore: false,
  args: [],
  columns: ['status', 'platform', 'account', 'account_id'],
  func: async (page) => {
    const cookie = await getCookieHeader(page, ['https://baijiahao.baidu.com/']);
    const result = await request(`https://baijiahao.baidu.com/builder/app/appinfo?_=${Date.now()}`, {
      headers: { Cookie: cookie, Origin: 'https://baijiahao.baidu.com', Referer: 'https://baijiahao.baidu.com/' },
    });
    assertHttp(result.response, result.text, '检查百家号登录账号');
    const data = parseJson(result.text, '检查百家号登录账号');
    const user = data?.data?.user;
    if (!user?.userid) throw new CliError('AUTH_REQUIRED', '未识别到百家号登录账号');
    return accountResult({ platform: 'baijiahao', account: user.name || user.userid, accountId: user.userid });
  },
});
