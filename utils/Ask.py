import questionary
from typing import Any

class Ask:
    """questionary 封装类"""
    def prompt_text(self, message: str, default: str = "") -> str:
        """提示用户输入文本"""
        return questionary.text(message, default=default).ask()
    def prompt_password(self, message: str, default: str = "") -> str:
        """提示用户输入文本"""
        return questionary.password(message, default=default).ask()
    def prompt_select(self, message: str, choices: list[tuple[str, Any]], default: Any = None) -> Any:
        """
        提示用户从选项中选择，返回选项对应的 key/值
        
        参数:
            message: 提示信息
            choices: 选项列表，格式为 [(显示文字, 对应值), ...]
            default: 默认选择的对应值
            
        返回:
            用户选择的选项对应的值
        """
        # 创建显示文字列表
        display_choices = [display for display, _ in choices]
        
        # 根据默认值找到对应的显示文字
        default_display = None
        if default is not None:
            for display, value in choices:
                if value == default:
                    default_display = display
                    break
        
        # 提示用户选择
        selected_display = questionary.select(
            message,
            choices=display_choices,
            default=default_display,  # 显示文字作为默认选择
        ).ask()
        
        # 根据选择的显示文字查找对应的值
        for display, value in choices:
            if display == selected_display:
                return value
        
        # 正常情况下不会执行到这里
        return None

    def prompt_yesNo(self,message:str) -> bool:
        '''
            选择的方式 yes or no
        '''
        return self.prompt_select(message,[
            ('是', "yes"), 
            ('否', "no")])=='yes'
    
    def prompt_confirm(self, message: str) -> bool:
        """提示用户确认操作"""
        return questionary.confirm(message).ask()