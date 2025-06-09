import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox
from get_path import get_actual_path

# 重度抑郁
severe_DrugProbability = "重度度抑郁障碍 寻求资深心理健康专家的全面评估与紧急干预。通过定制化的综合治疗计划，包括药物治疗、心理治疗（如认知行为疗法、心理教育等）、物理治疗（如经颅磁刺激等），以及必要时的住院治疗，来有效控制症状，减轻患者的痛苦。同时，建立稳定的社会支持系统，鼓励患者参与康复活动，逐步重建积极的生活态度和社交功能，以实现全面的心理康复和生活质量的显著提升，持续进行脑电后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.情绪极度低落绝望：持续悲伤，对快乐无感，丧失生活兴趣。\n2.认知功能显著减退：思维迟缓，注意力不集中，记忆力下降，自我评价低。\n3.生理与行为明显衰退：睡眠障碍，食欲改变，活动减少，甚至出现自杀念头。"

# 重度焦虑
severe_AnxietyProbabilit = "重度焦虑障碍 针对重度焦虑的严重情况，我们强烈建议患者及其家属积极行动起来，尽快寻求专业心理健康机构的全面评估与深入治疗。通过综合运用药物治疗、心理疗法（如认知行为疗法、放松训练等）以及必要时的物理疗法，来有效缓解焦虑症状，减轻患者的心理负担，持续进行后续脑电复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.情绪极度紧张不安：持续感到极度不安、紧张和强烈的恐惧感。\n2.躯体症状明显：伴随心跳加速、呼吸急促、出汗等明显的生理反应。\n3.生活质量受影响：日常生活、工作和学习能力严重受损，甚至可能出现轻生念头。"

# 重度成瘾
severe_DepressionProbability = "重度成瘾障碍 针对重度成瘾问题，强烈建议患者及家人尽快与专业医疗机构或成瘾治疗中心取得联系，寻求综合性、个性化的戒瘾治疗方案。这不仅包括针对成瘾物质或行为的生理脱瘾治疗，还应涵盖深入的心理干预、认知行为疗法、家庭支持疗法以及必要的康复训练和后续跟进。通过多层次的干预措施，旨在帮助患者从根本上摆脱成瘾的束缚，重建健康的生活模式，提升心理韧性和自我管理能力，持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.强迫性行为与渴求：对成瘾物质或行为有不可抗拒的强烈渴求和冲动。\n2.失去控制与功能受损:成瘾行为失控，严重影响日常生活和社会功能。\n3.戒断反应与心理依赖：停止成瘾行为后出现明显生理和心理反应，形成强烈心理依赖。"

# 中度
moderate_DrugProbability = "中度抑郁障碍 建议主动迈出步伐，积极寻求专业心理咨询或治疗，与专业人士共同制定个性化的康复计划。同时，不忘自我关爱，关注自己的身心需求，培养健康的生活习惯，如规律作息、均衡饮食和适量运动。保持积极的心态，参与有益的活动，与家人朋友保持联系，寻求社会支持。相信自己的能力和价值，坚持治疗，逐步缓解抑郁症状，持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.情绪持续低落：长时间感到悲伤、忧郁，对日常活动失去兴趣。\n2.认知与生理障碍：思维迟缓，注意力下降，伴随睡眠障碍、食欲改变等生理症状。\n3.社交与行为退缩：避免社交，可能出现消极念头或行为，精神运动性阻滞明显。"

moderate_AnxietyProbabilit = "中度焦虑障碍 对于中度焦虑，我们强烈建议主动寻求心理健康专家的帮助，通过专业的评估和治疗来有效管理症状。同时，学习并运用放松技巧、认知行为疗法等应对策略，以减轻焦虑感。调整日常生活方式，包括规律作息、健康饮食和适度运动，也是缓解焦虑的重要途径。通过这些综合措施，您可以更好地控制焦虑情绪，提高生活质量，持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.情绪紧张不安：持续担心、紧张害怕，无明确对象。\n2.躯体症状明显：自主神经功能紊乱，多系统不适。\n3.生活质量受影响：效率低下，注意力难集中，睡眠障碍。"

moderate_DepressionProbability = "中度成瘾障碍 针对中度成瘾问题，我们强烈建议成瘾者及其家人立即采取行动，积极寻求专业的医疗和心理咨询支持。通过综合的治疗方法，包括药物治疗、心理干预和行为疗法等，帮助成瘾者逐步减少并最终戒除成瘾行为。同时，提供持续的心理支持和康复指导，帮助成瘾者重建健康的生活习惯，增强自我控制能力，以全面恢复身心健康，重新融入社会，持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状：\n1.强烈欲望与依赖：对成瘾物质或行为有强烈需求，难以摆脱。\n2.机体损害与功能障碍:健康受损，生活与工作效率下降。\n3.无法自控与戒断反应：明知有害却无法停止，戒断时症状明显。"

# 正常
normal_DrugProbability = "预防抑郁障碍 积极关爱自我，保持乐观向上的心态，均衡安排生活，培养健康习惯，勇于面对挑战，享受生活中的每一个美好瞬间，让心灵充满阳光，拥抱健康与持久的幸福。"

normal_AnxietyProbabilit = "预防焦虑障碍 学会放下心中的重担，保持一颗平和而坚韧的心，用乐观的态度面对生活的起伏。避免无谓的焦虑侵扰，专注于当下的美好，珍惜每一刻的宁静与自在。让心灵得到真正的放松，享受由内而外的平和与幸福。"

normal_DepressionProbability = "预防成瘾障碍 保持清醒头脑，珍爱自我健康与自由，警惕任何可能导致成瘾的行为或物质。培养积极、有益的生活习惯，追求身心平衡与和谐发展。通过自我觉察与意志力，远离成瘾的陷阱，享受自由、充实且有意义的生活。"

# 轻度
mild_DrugProbability = "轻度抑郁障碍 建议尝试在日常生活中寻找并培养个人兴趣爱好，这些活动能够激发积极情绪，为生活增添色彩。其次,保持与亲朋好友的社交联系，分享彼此的快乐与困扰，可以获得情感上的支持和理解。同时，关注自我情绪变化，学会识别并合理表达负面情绪，避免情绪积压。此外，保持规律的作息时间和健康的生活习惯，如适量运动、均衡饮食和充足睡眠，也对缓解抑郁症状有积极作用,持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状:\n1.情绪持续低落:情绪低落，兴趣减退。\n2.认知与生理障碍:精力不足，易疲劳。\n3.社交与行为退缩:自我价值感降低，消极思维增多。"

mild_AnxietyProbabilit = "轻度焦虑障碍 建议学习并实践放松技巧，如深呼吸、冥想、瑜伽等，这些活动有助于缓解身体的紧张感，使心灵得到平静。其次，保持积极乐观的心态，关注自身的优点和成就，避免陷入消极的思维循环中。通过培养兴趣爱好、参与社交活动等方式，可以转移注意力，增加生活的乐趣和满足感，持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状:\n1.情绪紧张不安:过度担忧与紧张。\n2.躯体症状明显: 注意力难以集中。\n3.生活质重受影响:身体紧张反应，如心悸、胸闷。"

mild_DepressionProbability = "轻度成瘾障碍 建议认识到成瘾行为对个人生活产生的负面影响，并设定明确的目标来减少或戒除这种行为。其次，逐步调整日常生活习惯，增加健康有益的活动，如运动、阅读、社交等，以替代成瘾行为所占据的时间和精力。同时，寻求家人、朋友或专业人士的支持和帮助，共同制定并执行一个可行的计划，以逐步减少依赖并最终摆脱成瘾的困扰,持续进行后续复查与评估，确保康复进展，及时调整治疗方案。\n典型症状:\n1.强烈欲望与依赖:对成瘾物质或行为有强烈需求，难以摆脱。\n2.机体损喜与功能障碍:健康受损，生活与工作效率下降。\n3.无法自控与戒断反应:明知有害却无法停止，戒断时症状明显。"

report = "1.本检测不适用于临床诊断，本检测只从脑波层面上进行评估，因不涉及其他因素的考虑， 不代表您的真实情况；\n2.受限于现有科技手段和科学认知水平，该检测可能不能覆盖所有脑波及情况；\n3.以上建议及方案仅供初步分析使用，深度分析请咨询专业测评师。"


def wait_noblock(cnt=0.1, interval=0.02, flg_exit=False):
    """不阻塞等待
    参数：
        cnt:多少个0.1秒
        flg_exit:为true,立即退出等待
        interval:每次等待的间隔时间
    """
    if flg_exit:
        return
    iterations = int(cnt / interval)
    for _ in range(iterations):
        QApplication.processEvents()
        time.sleep(interval)


def wait_noblock_(interval=0.002):
    """不阻塞等待
    参数：
        cnt:多少个0.1秒
        flg_exit:为true,立即退出等待
        interval:每次等待的间隔时间
    """
    for _ in range(5):
        QApplication.processEvents()
        time.sleep(interval)

    # if cnt == 0:
    #     QApplication.processEvents()
    #     return
    # for i in range(cnt):
    #     for t in range(5):
    #         if flg_exit:
    #             return
    #         QApplication.processEvents()
    #         time.sleep(0.02)


def definition_MessageBox(text):
    msg_box = QMessageBox()
    msg_box.setWindowTitle('提示')
    msg_box.setWindowIcon(QIcon(":/icon/res/logo.png"))
    msg_box.setIcon(QMessageBox.Information)
    message_text = f'<font color="black">{text}</font>'
    msg_box.setText(message_text)
    msg_box.setStyleSheet("QMessageBox { background-color: white;}")
    # 添加按钮
    yes_button = msg_box.addButton(QMessageBox.Yes)
    yes_button.setText('确定')
    msg_box.exec_()


def select_definition_MessageBox(text):
    msg_box = QMessageBox()
    msg_box.setWindowTitle('提示')
    ico_path = get_actual_path(":/icon/res/jk.ico")
    msg_box.setWindowIcon(QIcon(ico_path))
    msg_box.setIcon(QMessageBox.Information)
    message_text = f'<font color="black">{text}</font>'
    msg_box.setText(message_text)
    msg_box.setStyleSheet("QMessageBox { background-color: white;}")

    # 添加“否”按钮
    no_button = msg_box.addButton(QMessageBox.Yes)
    no_button.setText('否')

    # 添加“是”按钮
    yes_button = msg_box.addButton(QMessageBox.No)
    yes_button.setText('是')

    # 设置“是”按钮为默认按钮
    msg_box.setDefaultButton(yes_button)

    # 去掉关闭窗口的图标
    msg_box.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

    # 显示消息框
    msg_box.exec_()
    return msg_box, yes_button, no_button
