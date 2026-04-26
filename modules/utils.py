GoalCn = ["平手", "平手/半球", "半球", "半球/一球", "一球", "一球/球半",
          "球半", "球半/两球", "两球", "两球/两球半", "两球半", "两球半/三球",
          "三球", "三球/三球半", "三球半", "三球半/四球", "四球", "四球/四球半",
          "四球半", "四球半/五球", "五球", "五球/五球半", "五球半", "五球半/六球",
          "六球", "六球/六球半", "六球半", "六球半/七球", "七球", "七球/七球半",
          "七球半", "七球半/八球", "八球", "八球/八球半", "八球半", "八球半/九球",
          "九球", "九球/九球半", "九球半", "九球半/十球", "十球", "十球/十球半",
          "十球半", "十球半/十一球", "十一球", "十一球/十一球半", "十一球半",
          "十一球半/十二球", "十二球", "十二球/十二球半", "十二球半",
          "十二球半/十三球", "十三球", "十三球/十三球半", "十三球半",
          "十三球半/十四球", "十四球"]

GoalOU = ["0", "0/0.5", "0.5", "0.5/1", "1", "1/1.5", "1.5", "1.5/2", "2", "2/2.5",
          "2.5", "2.5/3", "3", "3/3.5", "3.5", "3.5/4", "4", "4/4.5", "4.5", "4.5/5",
          "5", "5/5.5", "5.5", "5.5/6", "6", "6/6.5", "6.5", "6.5/7", "7", "7/7.5",
          "7.5", "7.5/8", "8", "8/8.5", "8.5", "8.5/9", "9", "9/9.5", "9.5", "9.5/10",
          "10", "10/10.5", "10.5", "10.5/11", "11", "11/11.5", "11.5", "11.5/12",
          "12", "12/12.5", "12.5", "12.5/13", "13", "13/13.5", "13.5", "13.5/14", "14"]

GoalOU2 = ["0", "0/-0.5", "-0.5", "-0.5/-1", "-1", "-1/-1.5", "-1.5", "-1.5/-2",
           "-2", "-2/-2.5", "-2.5", "-2.5/-3", "-3", "-3/-3.5", "-3.5", "-3.5/-4",
           "-4", "-4/-4.5", "-4.5", "-4.5/-5", "-5", "-5/-5.5", "-5.5", "-5.5/-6",
           "-6", "-6/-6.5", "-6.5", "-6.5/-7", "-7", "-7/-7.5", "-7.5", "-7.5/-8",
           "-8", "-8/-8.5", "-8.5", "-8.5/-9", "-9", "-9/-9.5", "-9.5", "-9.5/-10",
           "-10"]

_cn_nums = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
            "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十"]


def _build_cn(goal_val):
    n = int(abs(goal_val))
    if n >= len(_cn_nums):
        return str(n)
    return _cn_nums[n]


def _goal_cn_dynamic(goal_val):
    n = int(abs(goal_val) * 4)
    if n < len(GoalCn):
        return GoalCn[n]
    whole = int(abs(goal_val))
    frac = abs(goal_val) - whole
    cn = _build_cn(whole)
    if frac == 0:
        return cn + "球"
    elif frac == 0.25:
        return cn + "球/" + cn + "球半"
    elif frac == 0.5:
        return cn + "球半"
    elif frac == 0.75:
        nxt = _build_cn(whole + 1)
        return cn + "球半/" + nxt + "球"
    return f"{abs(goal_val)}"


def _goal_ou_dynamic(goal_val):
    n = int(abs(goal_val) * 4)
    if goal_val >= 0:
        if n < len(GoalOU):
            return GoalOU[n]
        return f"{abs(goal_val)}"
    else:
        if n < len(GoalOU2):
            return GoalOU2[n]
        return f"-{abs(goal_val)}"


def goal2goal_cn(goal_str):
    if not goal_str or goal_str.strip() == '':
        return ''
    try:
        goal = float(goal_str)
        text = _goal_cn_dynamic(goal)
        if goal < 0:
            return "受让" + text
        return text
    except (ValueError, TypeError):
        return goal_str


def goal2goal_ou(goal_str):
    if not goal_str or goal_str.strip() == '':
        return ''
    try:
        goal = float(goal_str)
        return _goal_ou_dynamic(goal)
    except (ValueError, TypeError):
        return goal_str
