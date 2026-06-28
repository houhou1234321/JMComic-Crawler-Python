from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''

1425887   
1425702   
1424820   
1231698   
1230557   
1427037
1437879   
1415513   
1242562   
1242300   
1239240   
1220658   
1209616   
1200177   
479819    
478480    
655018    
654094    
305898    
202939    
140707    
169853    
149854    
145263    
114872    
1415464   
558152    
557926    
557754    
557520    
557344    
381147    
112627    
99954     
25182     
23032     
1400916   
1246213   
1216909   
1210485   
1023163   
1014238   
629885    
628401    
626602    
626601    
619552    
619537    
1005999   
992030    
986494    
533791    
532551    
525527    
510158    
510157    
477664    
477250    
1443340   
1443341   
1442284   
1332298   
1234934   
1211977   
1211806   
1227056   
1415919   
1374591   
1282576   
1282571   
1258319   
1255804   
1239129   
1224177   
1194742   
1187381   
1173025   
1156336   
1079841   
1077915   
1054302   
1053599   
1052812   
1052911   
1051405   
1032520   
1097024   
1028964   
1096990   
1025008   
1014214   
1003544   
602619    
569636    
561566    
554957    
507041    
530541    
452853    
511737    
510041    
251293    
501661    
430793    
1443510   
1441888   
1440884   
1422844   
1370542   
1352214   
1282268   
1255337   
1255153   
1239381   
1216636   
1211588   
1208273   
1447919   
1255732   
1204031   
1095552   
1060358   
1019270   
645643    
645563    
528928    
484202    
 484201   
 484200   
 484199   
 483360   
 483357   
 483356   
 483354   
 483353   
481169    
470677    
401649    
359847    
1252639   
 1236351  
 1061364  
 
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
