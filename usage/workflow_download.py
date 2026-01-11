from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''

1209542
1208329
1178244
1114928
1110742
1102274
1082833
1014625
618819
573038
570425
558144
548971
543253
539476
527466
527325
1243884
1243039
1239381
1216636
1211588
1211405
1208273
1207979
1207449
1199599
1199598
1199597
1199511
1081662
1067688
1067685
1052886
1052885
1052884
1051886
1050798
1047423
1046523
1022426
551074
1245592
1243981
1243670
1243376
1226027
1213444
1211892
1207560
1207468
1207201
1192981
1191270
1188772
1188029
1178603
1243220
1214406
1208643
1244572
1244441
1206668
1197586
1191920
1088202
1054221
1052269
617874
1241093
1206640
1174591
1124247
1035904
635444
1246883
1243050
1205988
1048129
618695
616551
526069
524881
501939
501938
377484
481176
478032
447533
416385
415524
413000
375649
342596
263473
225291
206355
135965
1245517
1244434
1232276
1208736
1207502
1202118
1198896
1190043
1184463
1183420
1182480
1069332
1051200
1050590
1050546
1211808
1211524
1169861
1063644
1060259
631939
631275
589379
570434
567956
479570
455034
431845
431726
370746
364875
340340
307148
305878
301406
297276
246308
221658
187080
149439
148851
144918
143218
107248
105551
44621
41141
38825
32881
32151
32118
30881
30877
30682
30530
30529
29469
22699
22681
21815
9905
5873
5020
1103
1211808
1211524
1169861
1063644
1060259
631939
631275
589379
570434
567956
479570
455034
431845
431726
370746
364875
340340
307148
305878
301406
297276
246308
221658
187080
149439
148851
144918
143218
107248
105551
44621
41141
38825
32881
32151
32118
30881
30877
30682
30530
30529
29469
22699
22681
21815
9905
5873
5020
1103

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
