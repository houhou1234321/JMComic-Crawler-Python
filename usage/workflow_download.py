from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''

    1243744   
  1214212   
  1206643   
  1051117   
  1048728   
  640480    
  616523    
   1251655  
   1438281  
  1436969   
  1256406   
  1251347   
  1211524   
  1169861   
   1436950  
  1429343   
  1429342   
  1428653   
  1370783   
  1336817   
  1207533   
  1255641   
  1229547   
  1221894   
  1221890   
  1220653   
  1220651   
  1202001   
  1199760   
  1187977   
  1166101   
  1166100   
  1148993   
  1128212   
  1085152   
  1070370   
  1070369   
  1070368   
  1070367   
  1070366   
  1070363   
  1070362   
  1070361   
  1070360   
  1070359   
  1070357   
  1070356   
  1070355   
  1070354   
  1070353   
  1070352   
  1070351   
  1066912   
  1043081   
  1036349   
   1434891  
  1394754   
  1255466   
  1235891   
  1223980   
  1185399   
  1053394   
  1051198   
  1050079   
  1049628   
  1043092   
  639561    
  576700    
  572814    
  565952    
  446024    
  446023    
  443451    
  435227    
  433478    
  433235    
  433234    
  433233    
  433232    
  411791    
  411790    
  400630    
   1236729  
  1090172   
  1058037   
  1028404   
  1020584   
  1017578   
  642677    
  623449    
  586485    
  554743    
  459361    
  419980    
   1175041  
  583214    
  500005    
  495324    
  404474    
  340550    
  366813    
  294568    
  292418    
  264883    
  100516    
  142809    
   1338869  
  1259226   
  1241984   
  1241499   
  1095381   
  645301    
  544851    
  539454    
  496414    
  421058    
  372787    
  372619    
  371878    
  371637    
  316563       
 
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
