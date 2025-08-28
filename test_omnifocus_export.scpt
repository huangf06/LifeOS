-- OmniFocus 数据导出测试脚本
-- 用于验证数据导出功能

tell application "OmniFocus 3"
    -- 获取所有未完成的任务
    set allTasks to every flattened task of default document whose completed is false
    
    set taskCount to count of allTasks
    display dialog "找到 " & taskCount & " 个未完成任务" buttons {"继续", "取消"} default button "继续"
    
    if button returned of result is "继续" then
        set taskList to ""
        
        -- 遍历前10个任务（避免输出过多）
        repeat with i from 1 to (count of allTasks)
            if i > 10 then exit repeat
            
            set currentTask to item i of allTasks
            set taskName to name of currentTask
            set taskCompleted to completed of currentTask
            
            -- 获取项目名称
            set projectName to "Inbox"
            try
                set projectName to name of containing project of currentTask
            end try
            
            -- 获取截止日期
            set dueInfo to "无截止日期"
            try
                set dueDate to due date of currentTask
                set dueInfo to dueDate as string
            end try
            
            -- 组装任务信息
            set taskInfo to i & ". " & taskName & "\n"
            set taskInfo to taskInfo & "   项目: " & projectName & "\n"
            set taskInfo to taskInfo & "   截止: " & dueInfo & "\n"
            set taskInfo to taskInfo & "   完成: " & taskCompleted & "\n\n"
            
            set taskList to taskList & taskInfo
        end repeat
        
        -- 显示结果
        display dialog taskList buttons {"保存到文件", "完成"} default button "保存到文件"
        
        if button returned of result is "保存到文件" then
            -- 保存到桌面
            set desktopPath to (path to desktop as string) & "OmniFocus_Export_Test.txt"
            set fileRef to open for access file desktopPath with write permission
            set eof of fileRef to 0
            write taskList to fileRef
            close access fileRef
            
            display notification "数据已导出到桌面" with title "OmniFocus Export" sound name "Glass"
        end if
    end if
end tell