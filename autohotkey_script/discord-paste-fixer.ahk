; Discord に Ctrl+V で貼り付けるときだけ、クリップボード中の URL を変換して貼り付ける。
; 他のアプリでの貼り付けには影響しない。貼り付け後はクリップボードを元に戻す。
#Requires AutoHotkey v2.0
#SingleInstance Force

; 変換ルール（正規表現, 置換後）。上から順に適用する
RULES := [
    ["i)\bhttps?://(?:www\.)?(?:x|twitter)\.com/", "https://fxtwitter.com/"],
]

GroupAdd("Discord", "ahk_exe Discord.exe")
GroupAdd("Discord", "ahk_exe DiscordPTB.exe")
GroupAdd("Discord", "ahk_exe DiscordCanary.exe")

ConvertText(text) {
    for rule in RULES
        text := RegExReplace(text, rule[1], rule[2])
    return text
}

#HotIf WinActive("ahk_group Discord")
$^v:: {
    ; 画像などテキスト以外のときは A_Clipboard が空になるので、そのまま貼り付ける
    original := A_Clipboard
    converted := ConvertText(original)
    if (original = "" || converted == original) {
        Send("^v")
        return
    }

    saved := ClipboardAll()
    A_Clipboard := converted
    if !ClipWait(1) {
        A_Clipboard := saved
        Send("^v")
        return
    }
    Send("^v")
    ; 貼り付けが終わる前に戻すと元の内容が貼られるので、少し待ってから戻す
    Sleep(300)
    A_Clipboard := saved
}
#HotIf
