from comastore_ocr.convert import convert_json_dir_to_jsonl


def main() -> None:
    processed, errors, output_path = convert_json_dir_to_jsonl()
    print("\n🎉 Processing complete!")
    print(f"✅ Successfully processed: {processed} files")
    print(f"❌ Errors: {errors} files")
    print(f"📄 Output saved to: {output_path}")


if __name__ == "__main__":
    main()

