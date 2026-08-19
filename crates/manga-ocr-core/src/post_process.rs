/// Japanese text normalization post-processing function.
/// Replaces ellipsis variants and converts ASCII digits/letters to Japanese full-width (jaconv h2z equivalent).
pub fn post_process(input: &str) -> String {
    let mut result = String::with_capacity(input.len());
    let normalized = input.replace('…', "...");

    for ch in normalized.chars() {
        match ch {
            // ASCII printable range '!' (0x21) to '~' (0x7E) mapped to full-width (0xFF01 to 0xFF5E)
            '!'..='~' => {
                let fullwidth_code = (ch as u32) + 0xFEE0;
                if let Some(fw_char) = char::from_u32(fullwidth_code) {
                    result.push(fw_char);
                } else {
                    result.push(ch);
                }
            }
            // Space ' ' (0x20) mapped to full-width space '　' (0x3000)
            ' ' => result.push('　'),
            _ => result.push(ch),
        }
    }

    result.trim().to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_post_process_ellipsis_and_fullwidth() {
        assert_eq!(post_process("…"), "．．．");
        assert_eq!(post_process("テスト 123"), "テスト　１２３");
        assert_eq!(post_process("Hello!"), "Ｈｅｌｌｏ！");
    }
}
