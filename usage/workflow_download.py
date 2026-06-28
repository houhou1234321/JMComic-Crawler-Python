from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''

  1447311     
  1444131     
  1443311     
  1252160     
  1246524     
  1245982     
  1245572     
  70616       
  1207697     
  1149370     
  554252      
  1094464     
  1048188     
  1046549     
  1042137     
  648591      
  531044      
  527309      
  526646      
  526441      
  526439      
  499287      
  499286      
  452219      
  408130      
  404785      
  221720      
  380437      
  379065      
  371856      
  333901      
  208629      
  307005      
  292763      
  289747      
  61235       
  289746      
  289745      
  289744      
  289743      
  289741      
  280336      
  254916      
  241550      
  231468      
  218622      
  217842      
  206632      
  147227      
  142464      
  129981      
  124413      
  122735      
  122586      
  122279      
  122278      
  116265      
  113907      
  112708      
  105863      
  99083       
  76796       
  71952       
  71937       
  61218       
  54779       
  54352       
  43271       
  43117       
  43026       
  33856       
  33738       
  33715       
  33589       
  33470       
  33460       
  33136       
  29625       
  29600       
  26730       
  1251861     
  1233462     
  1233499     
  1190051     
  517813      
  1162721     
  1162720     
  429914      
  477165      
  480370      
  1124505     
  1060364     
  1058163     
  1038286     
  493995      
  1099102     
  1045710     
  1038287     
  1026689     
  1026303     
  1020525     
  1020524     
  1020523     
  581627      
  549183      
  547183      
  533139      
  531102      
  527780      
  517822      
  508780      
  504761      
  502928      
  502919      
  502259      
  502258      
  489835      
  475609      
  474080      
  468758      
  458748      
  422543      
  420661      
  418770      
  416438      
  415981      
  410296      
  401426      
  386745      
  370882      
  359603      
  346611      
  345026      
  270328      
  330983      
  330759      
  330770      
  301990      
  301987      
  301986      
  301985      
  282680      
  279129      
  272075      
  230262      
  229070      
  198058      
  196335      
  213220      
  196163      
  138639      
  195500      
  137433      
  113433      
  107189      
  103802      
  103553      
  103376      
  97870       
  73529       
  1422823     
  1238802     
  1190484     
  1107544     
  1038978     
  437703      
  437701      
  373967      
  364550      
  324473      
  275510      
  217586      
  1438411     
  1247164     
  1204050     
  1448062     
  1247006     
  1211528     
  1043011     
  629915      
  594134      
  540388      
  539439      
  523243      
  514095      
  512645      
  1246051     
  1208954     
  361065      
  200068      
  145311      
  104623      
   1245535    
  1190040     
  1189651     
  527128      
  410030      
  290896      
  1245094     
  1248177     
  1222169     
  1211302     
  1195743     
  1164314     
  1036702     
  1446168     
  1254816     
  1245284     
  1075062     
  614512      
  490864      
  1247697     
  1247432     
  1242724     
  1229519     
  1221869     
  1156288     
  508676      
  481463      
  480793      
  480758      
  408075      
  372803      
  372644      
  369452      
  305830      
  303159      
  303048      
  149901      
  146802      
  146797      
  146796      
  140356      
  125608      
  125607      
  125429      
  124084      
  124083      
  123957      
  119372      
  119369      
  119368      
  119356      
  117052      
  114409      
  114026      
  103733      
  73432       
  73426       
  71270       
  70902       
  70559       
  70422       
  70414       
  70329       
  70309       
  70300       
  70283       
  70254       
  70244       
  70167       
  70162       
  70157       
  68657       
  68482       
  66808       
  65281       
  60303       
  58565       
  58496       
  56469       
  52302       
  51854       
  51514       
  45774       
  44424       
  44423       
  44421       
  44418       
  44416       
  41730       
  40087       
  40086       
  40085       
  40083       
  40082       
  40081       
  40079       
  40078       
  40077       
  40076       
 
'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
