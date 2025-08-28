-- 测试获取今日完成的任务
-- 验证完成状态追踪功能

tell application "OmniFocus 3"
    set todayStart to current date
    set hours of todayStart to 0
    set minutes of todayStart to 0
    set seconds of todayStart to 0
    
    set todayEnd to todayStart + (24 * 60 * 60) - 1
    
    -- 获取今日完成的任务
    set completedToday to every flattened task of default document whose completed is true and completion date ≥ todayStart and completion date ≤ todayEnd
    
    set completedCount to count of completedToday
    
    if completedCount = 0 then
        display dialog "今天还没有完成任何任务" buttons {"OK"}
    else
        set completedList to "今日完成的任务 (" & completedCount & "个):\n\n"
        
        repeat with currentTask in completedToday
            set taskName to name of currentTask
            set completionTime to completion date of currentTask
            
            set completedList to completedList & "✅ " & taskName & "\n"
            set completedList to completedList & "   完成时间: " & completionTime & "\n\n"
        end repeat
        
        -- 显示结果
        display dialog completedList buttons {"保存", "关闭"} default button "保存"
        
        if button returned of result is "保存" then
            set desktopPath to (path to desktop as string) & "Today_Completed_Tasks.txt"
            set fileRef to open for access file desktopPath with write permission
            set eof of fileRef to 0
            write completedList to fileRef
            close access fileRef
            
            display notification "今日完成任务已导出" with title "OmniFocus Export"
        end if
    end if
end tell