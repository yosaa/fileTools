import os
import random
import sys
import io
from PIL import Image
import shutil
from pathlib import Path

# Try to import rembg, handle error if not available
try:
    import rembg
    # 获取用户目录
    user_dir = Path.home()
    target_dir = user_dir / ".u2net"
    target_path = target_dir / "u2net.onnx"
    
    # 检查目标目录是否存在，不存在则创建
    target_dir.mkdir(exist_ok=True)
    
    # 当前目录下的模型文件路径
    current_model = Path("u2net.onnx")
    
    # 检查当前目录是否存在模型文件
    if current_model.exists():
        # 检查目标位置是否已存在模型文件
        if target_path.exists():
            print(f"模型文件已存在于: {target_path}")
        else:
            # 移动文件到目标位置
            shutil.copy(str(current_model), str(target_path))
            print(f"模型文件已移动到: {target_path}")
    else:
        print(f"当前目录下未找到 u2net.onnx 文件: {current_model.absolute()}")
    REMBG_AVAILABLE = True 
except ImportError:
    REMBG_AVAILABLE = False
    print("警告: 未安装rembg库，将使用简单背景替换")
    print("请运行process_images.bat安装所需库")
    print()

def process_images(input_folder, overwrite_original=False, callback=None):
    """
    处理指定文件夹根目录中的图片，不处理子文件夹
    
    Args:
        input_folder: 输入文件夹路径
        overwrite_original: 是否覆盖原图，如果为False则创建新文件
        callback: 进度回调函数，格式为 callback(message)
    """
    # Counter for processed images
    processed_count = 0
    
    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    
    progress_messages = [
        "我处理得手都抽筋了，你倒是来帮我啊？",
        "图片这么多你是不想让我下班吧？",
        "救命，我又看到一张图飞过来了！",
        "你这文件夹是不是吃饱了撑的？",
        "慢慢来，再急也快不了。",
        "我这不是在摸鱼，是在蓄力！",
        "这张图好丑，我处理的时候吓了一跳。",
        "为什么图片永远处理不完？是谁的阴谋？",
        "等下，我喝口水压压惊。",
        "这活儿又累又苦，还不给加班费。",
        "如果处理图能减肥，我现在已经是纸片人了。",
        "你的图片太多，我开始怀疑人生。",
        "我现在只想假装死机。",
        "不解释，我就是在努力……不用怀疑。",
        "我不是慢，我是优雅。",
        "这张图看着就很难搞。",
        "我在处理，但我的心在躺平。",
        "谁能告诉我为什么图片比我朋友还多？",
        "别催我，我已经是光速了。",
        "你以为我是人工智能？我是人工累死。",
        "哦？又来一张？是图对吧？不是炸弹吧？",
        "再处理两张我就下线罢工了。",
        "你把我当廉价劳动力了吗？",
        "我努力装作专业的样子。",
        "糟了，我的 CPU 都开始冒热气了。",
        "我现在是名副其实的图奴隶。",
        "别着急，急也没用。",
        "我需要一个假期，就现在。",
        "一张、一张、又一张……无尽循环。",
        "我处理得都快产生幻觉了。",
        "你再加图我就报警了啊！",
        "我现在只想睡觉，图片你自己处理吧？",
        "我感觉我正在被这些图吸走生命力。",
        "请善待我，我也很脆弱的。",
        "来个赞也行啊，我这么努力。",
        "我能不能摸条鱼再继续？",
        "抱歉，我在加载情绪值。",
        "这张图……我不想评价，懂的都懂。",
        "我不是卡了，是我累了。",
        "图太多，会崩，会累，会想退休。",
        "不瞒你说，我已经处理到麻木了。",
        "我已经进入自动打工模式。",
        "让我缓一下，这批图有点社会我害怕。",
        "烦死了，这张图怎么又来？",
        "等等，我又懵了。",
        "我努力让自己看起来很在线。",
        "图来了，我的心却走了。",
        "这不是处理图片，这是修行。",
        "你这是把我当苦力使唤啊。",
        "我已经开始怀疑图是不是长出来的。",
        "你到底有多少张图？说实话！",
        "再来十张我可能会断开链接。",
        "请问我啥时候能处理完？",
        "今天的我：累但继续。",
        "图片……为什么你要这样对我。",
        "加载中，其实我在偷懒。",
        "想装死，但还得继续处理。",
        "我的鼠标都在流汗了。",
        "有时候我也想对图片说：放过我吧！",
        "你发誓这些图不是复制粘贴出来的吗？",
        "你就是想看我累对吧？",
        "再多我真的会变成表情包。",
        "这速度已经超越乌龟了！",
        "我有点想离职了。",
        "你要不要考虑删点图？",
        "我感觉我被压迫了。",
        "一点点处理，心态一点点炸裂。",
        "我脑袋都成 jpg 格式了。",
        "是图片太多，还是我太弱？我不知道。",
        "好好好，你的图我处理，你别骂我。",
        "处理中……其实我在叹气。",
        "有一说一，这图挺折磨我的。",
        "你真的不考虑给我发工资吗？",
        "救救孩子吧，这图太狠了。",
        "我想静静，但图不让我静静。",
        "我怀疑你在搞笑，但我没有证据。",
        "好嘞，又来一张，我认命了。",
        "别催了，再催我发脾气了！",
        "图片界的魔王出现了！",
        "这张图处理完，我休息三秒。",
        "你这些图是不是从外太空运来的？",
        "我正在熬过人生中最难的一批图。",
        "你把我 CPU 烧了不负责啊？",
        "我怀疑你是想让我罢工。",
        "我处理图的速度取决于我的心情。",
        "我现在是“半死不活”模式。",
        "这张图让我心态轻微崩溃。",
        "好吧，我继续挣扎。",
        "你听见了吗？那是我崩溃的声音。",
        "我真的太难了，你懂不懂。",
        "放心吧，我还能再坚持五分钟。",
        "我很累，但我不能说。",
        "这张图让我陷入深思：为什么要处理图？",
        "你再多给几张，我就直接跑了。",
        "我看到了希望……不，搞错了，是下一张图。",
        "努力处理，偶尔怀疑人生。",
        "兄弟，我真的是尽力了。",
        "没事，我还能处理，但别太多……拜托。",
        "我保证，这批图让我学会坚强。",
         "我怀疑你是不是把全公司图片都扔给我了。",
        "救命，我被图片淹没了，快递个救生圈来。",
        "这张图怎么看着有点欠揍？",
        "处理得我 CPU 都想辞职了。",
        "我现在是半自动打工人，请温柔点。",
        "你看这张图，它好像也不想被处理。",
        "别问我为啥慢，我在思考人生。",
        "我已经看不到尽头了，图片的尽头在哪里？",
        "我不是程序，我是图片苦力。",
        "你这是让我体验社畜人生？",
        "等一下，我的灵魂掉线了。",
        "真的假的？又来一张？",
        "我现在不想说话，只想安静处理图。",
        "我真的希望下一张是最后一张。",
        "我处理到怀疑这是不是在循环同一张图。",
        "兄弟，我真撑不住了。",
        "这活儿吧，说实话，我不太行。",
        "别催我，再催我就装死。",
        "我已经累到开始幻听了。",
        "图片太多，我已经跟它们混熟了。",
        "下一张请温柔一点。",
        "我突然理解了打工人的悲哀。",
        "图来了，我的心态走了。",
        "今晚我可能会梦到图片追着我跑。",
        "我嘴上说着可以，内心已经裂开。",
        "好家伙，这张图分量挺足啊。",
        "你知道吗？我已经彻底麻木了。",
        "请问图片也会长胖吗？怎么这么大？",
        "这张图一来，我的鼠标都抖了一下。",
        "我现在的状态：能动，但不多。",
        "温馨提示：我已经累到不温馨了。",
        "我要是再快点，图都怕我。",
        "图片这么多，是不是在搞我心态？",
        "我继续，你别讲话。",
        "深呼吸……我要上了！",
        "我正在努力隐藏我的崩溃。",
        "救命啊，这批图太离谱了。",
        "等一下，我需要一点精神力量。",
        "我现在的精神状况：自带马赛克。",
        "图片太多，我的耐心太少。",
        "你不会是打算一天处理完毕吧？",
        "我希望下一张是个善良的图。",
        "又来了，我叹了口气。",
        "这张图，我只能说很有攻击性。",
        "我不理解，这么多图你从哪搞来的？",
        "你是真不怕我辞职啊？",
        "我连抱怨的力气都快没了。",
        "我已经从“累”进阶到“麻木”。",
        "我轻声说一句：求放过。",
        "这张图看着就很想让我关机。",
        "我有预感，你这照片还没完。",
        "我的心态已经碎成小数点了。",
        "你可以慢慢添加，我可以慢慢崩溃。",
        "我已经进入自暴自弃模式。",
        "图片数量让我心寒。",
        "我需要一杯奶茶续命。",
        "处理图片这件事让我成长了……变强的那种痛。",
        "兄弟，我真不是超人。",
        "你听到我叹气了吗？那是绝望的声音。",
        "我看到下一张图，有种头皮发麻的感觉。",
        "图片太多会让人失去对生活的热爱。",
        "再来我真要下线躺平了。",
        "我现在看见 JPG 都害怕。",
        "打工魂在燃烧……但烧得不多。",
        "我不是慢，是图太多压得我喘不过气。",
        "刚处理完一张，又来了？你玩我呢？",
        "能不能给我发个红包安慰一下？",
        "这张图让我一秒变 emo。",
        "我已经在心里哭了八遍了。",
        "让我猜猜……下一张更离谱？",
        "你这图片是从地底挖出来的吗？怎么这么多？",
        "我有点疲惫，但我还在坚持。",
        "我现在怀疑自己是来打工的。",
        "不要问我为什么慢，我已经尽力了。",
        "我感觉自己像一台风扇，一直转一直转。",
        "让我缓三秒，我头晕了。",
        "我现在只希望图不要太大。",
        "我做梦都在处理图片，你信吗？",
        "你是想让我处理到天亮吗？",
        "这图尺寸大到离谱。",
        "我沉默了，但我在工作。",
        "这张图……我们不适合。",
        "努力处理，但精神逐渐枯萎。",
        "我也想摸鱼，但图不允许。",
        "这张图来势汹汹，我有点害怕。",
        "我已经从“烦”升级到“佛系”。",
        "这图让我感觉 CPU 在求饶。",
        "下一张图不要太复杂，我求你了。",
        "图片就像烦恼，一张接一张。",
        "我现在靠毅力在运转。",
        "我意识到：图永远不会自己处理。",
        "我想把这些图寄回去，让它们自己处理自己。",
        "我看着这张图，内心毫无波澜。",
        "又一张，又一张，我麻了。",
        "你知道吗？我真的累了。",
        "好吧，我继续干，但你得夸我一句。",
        "我怀疑这图在嘲笑我。",
        "处理中……但我的心已经躺平。",
        "你这是把我当永动机？",
        "我需要精神奖励，比如点赞。",
        "我现在是疲惫版处理器。",
        "算了，我认命了。",
        "图越多，我越想辞职。",
         "Hold on… my brain is buffering.",
        "Processing… but emotionally I'm not ready.",
        "Too many images, not enough motivation.",
        "I’m doing my best, which is not much today.",
        "These images are testing my patience.",
        "Who uploaded all of these? Who hurt you?",
        "My CPU is crying, please send help.",
        "Working… but I’d rather be napping.",
        "Another image? Oh joy…",
        "I didn’t sign up for this many pixels.",
        "Wait, I need a mental reboot.",
        "I swear these images are multiplying.",
        "Still processing… my soul left the chat.",
        "This one looks suspiciously heavy.",
        "I'm exhausted just looking at this picture.",
        "Why is this file so large? Why?",
        "Be patient, I'm fragile.",
        "Processing like a snail with back pain.",
        "One more image and I might revolt.",
        "My energy level is at 3%.",
        "You sure you need ALL these images?",
        "I miss my break already.",
        "Please stop throwing images at me.",
        "Processing… with tears.",
        "This image is fighting back.",
        "I'm convinced these files are cursed.",
        "Running… barely.",
        "Can I go home after this one?",
        "Image incoming… send prayers.",
        "Doing my job but not enjoying it.",
        "My processor regrets meeting you.",
        "Honestly, I’m struggling.",
        "Slow? No. Dramatically thoughtful.",
        "I didn't know suffering until today.",
        "If images had feelings, they’d hate me too.",
        "Okay fine… NEXT.",
        "This image looks complicated. I don't like it.",
        "Processing speed is directly related to my mood.",
        "You’re lucky I haven’t quit yet.",
        "Is this image made of dark matter? It's so heavy.",
        "Let me pretend I'm working fast.",
        "I think I just aged five years.",
        "My hopes are low, my workload is high.",
        "This is what digital pain feels like.",
        "Another one? Really?",
        "This picture is not giving good vibes.",
        "Working… but mentally I'm sunbathing.",
        "My circuits need a therapist.",
        "If I disappear, blame the images.",
        "Half working, half crying.",
        "I need coffee. And a raise.",
        "Processing… but my motivation left.",
        "I can't believe I'm still doing this.",
        "You good? Because I’m not.",
        "This image brought stress into my life.",
        "I wish I could delete myself.",
        "Warning: enthusiasm not found.",
        "You deserve a medal for having this many images.",
        "I'm not slow, I’m dramatic.",
        "I refuse to believe these images are normal.",
        "Give me a sec… I’m reconsidering everything.",
        "My will to work is running on fumes.",
        "This photo looks heavier than my life problems.",
        "If complaining burned calories, I'd be shredded.",
        "Processing… but trust me, I don’t want to.",
        "Why does this picture look like trouble?",
        "I’m so done and yet… here we are.",
        "My performance is proportional to my frustration.",
        "Please stop… I’m begging you.",
        "Another file? My spirit is tired.",
        "I feel underpaid for this… and I’m free.",
        "I shouldn’t have to work this hard for pixels.",
        "Thinking… mostly about quitting.",
        "Processing, but my heart isn't in it.",
        "I need a vacation from these images.",
        "Be right back, having an existential crisis.",
        "This image is bullying me.",
        "I’m overwhelmed and underpowered.",
        "Who knew image processing could be emotional?",
        "My patience bar is almost empty.",
        "Pretending to be okay… still processing.",
        "I miss the days when there were no images.",
        "Fine… I’ll do it, but I won’t be happy.",
        "This file is way too confident in itself.",
        "If I had legs, I'd walk away.",
        "Processing… and deeply regretting everything.",
        "The more I work, the less I want to.",
        "Not to alarm you, but I'm suffering.",
        "This image is suspiciously difficult.",
        "My internal fan just sighed loudly.",
        "I deserve a break after this one. And the next.",
        "This frequency of images should be illegal.",
        "I swear these files are pranking me.",
        "Processing like it's Monday morning.",
        "This is fine. Everything is fine. (It's not.)",
        "My efficiency is fictional.",
        "This image and I are not on speaking terms.",
        "I’m giving 20%, and that’s generous.",
        "Just processed one… why is there another?",
        "Okay but… when does it end?",
        "I’m convinced you hate me.",
        "Processing softly because I’m tired.",
        "Look at this image. It looks exhausting.",
        "I’m here physically, not mentally.",
        "I’ll survive… probably."
    ]



    
    # 获取根目录下的文件
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(supported_formats)]
    total = len(files)
    
    # 如果没有图片，直接返回
    if total == 0:
        if callback:
            callback("文件夹里没图片，搞啥呢？")
        return 0
     # 每次都要输出进度，但 message 不是每次都有
    message = ""
    # 处理根目录文件
    for filename in files:
        try:
            # Read the image
            input_path = os.path.join(input_folder, filename)
            
            if overwrite_original:
                output_path = input_path
            else:
                # 在根目录下创建"处理后图片"目录
                output_dir = os.path.join(input_folder, "处理后图片")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                # Keep original filename but change extension to .png
                output_filename = os.path.splitext(filename)[0] + '.png'
                output_path = os.path.join(output_dir, output_filename)
            
            print(f"Processing: {input_path}")
            
            if REMBG_AVAILABLE:
                # Read image as bytes
                with open(input_path, 'rb') as f:
                    input_bytes = f.read()
                
                # Remove background using rembg
                output_bytes = rembg.remove(input_bytes)
                
                # Convert result to PIL Image
                image = Image.open(io.BytesIO(output_bytes))
                
                # Place on white background
                white_bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
                white_bg.paste(image, mask=image.split()[-1])
                image = white_bg.convert("RGB")
            else:
                if callback:
                    callback("rembg 库未安装，背景移除不了！")
                return "rembg 库未安装，无法移除背景"
            
            # Crop to content (non-white pixels)
            bbox = image.getbbox()
            if bbox:
                # Crop to content
                cropped = image.crop(bbox)
            else:
                # If no content found, use the whole image
                cropped = image
            
            # 将主体放大150%，保持比例
            width, height = cropped.size
            
            # 计算放大150%后的尺寸
            new_width = int(width * 3)
            new_height = int(height * 3)
            
            # 确保不超过1000x1000画布
            scale_factor = min(1000 / new_width, 1000 / new_height, 1.0)
            if scale_factor < 1.0:
                new_width = int(new_width * scale_factor)
                new_height = int(new_height * scale_factor)
            
            # 放大图片
            resized = cropped.resize((new_width, new_height), Image.LANCZOS)
            
            # 创建 1000x1000 白底画布并居中贴图
            final_image = Image.new("RGB", (1000, 1000), (255, 255, 255))
            x = (1000 - new_width) // 2
            y = (1000 - new_height) // 2
            final_image.paste(resized, (x, y))
            
            # Add watermark if logo.jpg exists
            logo_path = "logo.jpg"
            if os.path.exists(logo_path):
                try:
                    logo = Image.open(logo_path).convert("RGBA")
                    # Reduce opacity to 30% (50% reduced by 20%)
                    logo_with_transparency = Image.new("RGBA", logo.size)
                    for x_wm in range(logo.size[0]):
                        for y_wm in range(logo.size[1]):
                            r, g, b, a = logo.getpixel((x_wm, y_wm))
                            logo_with_transparency.putpixel((x_wm, y_wm), (r, g, b, int(a * 0.3)))
                    
                    # Resize logo to 500x500 while maintaining aspect ratio
                    logo_width, logo_height = logo_with_transparency.size
                    max_logo_size = 500
                    if logo_width > logo_height:
                        new_logo_width = max_logo_size
                        new_logo_height = int(logo_height * max_logo_size / logo_width)
                    else:
                        new_logo_height = max_logo_size
                        new_logo_width = int(logo_width * max_logo_size / logo_height)
                    
                    logo_resized = logo_with_transparency.resize((new_logo_width, new_logo_height), Image.LANCZOS)
                    
                    # Paste logo in center
                    logo_x = (1000 - new_logo_width) // 2
                    logo_y = (1000 - new_logo_height) // 2
                    final_image = final_image.convert("RGBA")
                    final_image.paste(logo_resized, (logo_x, logo_y), logo_resized)
                    final_image = final_image.convert("RGB")
                except Exception as e:
                    print(f"Warning: Could not add watermark: {str(e)}")
            
            # 根据原始文件格式保存
            if overwrite_original:
                # 保持原始格式
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in ['.jpg', '.jpeg']:
                    final_image.save(output_path, 'JPEG', quality=95)
                elif file_ext == '.png':
                    final_image.save(output_path, 'PNG')
                elif file_ext == '.bmp':
                    final_image.save(output_path, 'BMP')
                elif file_ext in ['.tiff', '.tif']:
                    final_image.save(output_path, 'TIFF')
                elif file_ext == '.webp':
                    final_image.save(output_path, 'WebP')
                else:
                    final_image.save(output_path, 'PNG')
            else:
                # 保存为PNG格式
                final_image.save(output_path, 'PNG')
            
            print(f"Processed: {input_path}")
            processed_count += 1
            
            # 调用回调函数，随机选择一条日志
            if callback:
                # 每处理 5 张生成一句日志
                if processed_count % 3 == 0 or processed_count == total:
                    message = random.choice(progress_messages)
                if message:
                    callback(f"{message} ({processed_count}/{total})")
                else:
                    callback(f"({processed_count}/{total})")
            
        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
    
    print(f"Total processed images: {processed_count}")
    if callback and processed_count == total and total > 0:
        callback("终于搞定啦！累死我了，总共处理了 {} 张图！".format(processed_count))
    return processed_count

def process_folder(input_folder, overwrite_original=True, callback=None):
    """
    处理指定文件夹根目录中的图片
    
    Args:
        input_folder: 输入文件夹路径
        overwrite_original: 是否覆盖原图，默认为True
        callback: 进度回调函数，格式为 callback(message)
    """
    if not os.path.exists(input_folder):
        print(f"错误: 文件夹 {input_folder} 不存在")
        if callback:
            callback("文件夹不存在，检查下路径吧！")
        return 0
    
    print(f"开始处理文件夹: {input_folder}")
    if not REMBG_AVAILABLE:
        print("注意: 未检测到rembg库，将不进行背景移除")
        print("建议运行process_images.bat安装完整功能")
        if callback:
            callback("没装rembg，背景移除不了，赶紧去装！")
        print()
    else:
        print("正在移除背景并处理图片...")
        if callback:
            callback("Ready to rock! 开始处理图片啦！")
    
    count = process_images(input_folder, overwrite_original, callback)
    print(f"所有图片处理完成! 共处理 {count} 张图片")
    return count

if __name__ == "__main__":
    input_folder = "."
    output_folder = "./processed"
    print("Starting image processing...")
    if not REMBG_AVAILABLE:
        print("注意: 未检测到rembg库，将不进行背景移除")
        print("建议运行process_images.bat安装完整功能")
        print()
    else:
        print("This may take a while as it's removing backgrounds...")
    process_images(input_folder, False)  # 默认不覆盖原图
    print("All images processed!")
    input("Press Enter to exit...")