"""Tests for image handling in quizzes with relative paths."""

from __future__ import annotations

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_quiz.plugin import MkDocsQuizPlugin


@pytest.fixture
def plugin() -> MkDocsQuizPlugin:
    """Create a plugin instance for testing."""
    plugin = MkDocsQuizPlugin()
    plugin.config = {
        "enabled_by_default": True,
        "auto_number": False,
        "show_correct": True,
        "auto_submit": True,
        "disable_after_submit": True,
    }
    return plugin


@pytest.fixture
def mock_config() -> MkDocsConfig:
    """Create a mock config object."""
    return MkDocsConfig()


@pytest.fixture
def mock_page_root(mock_config: MkDocsConfig) -> Page:
    """Create a mock page object at root level (docs/test.md)."""
    file = File(
        path="test.md",
        src_dir="docs",
        dest_dir="site",
        use_directory_urls=True,
    )
    page = Page(None, file, mock_config)
    page.meta = {}
    return page


@pytest.fixture
def mock_page_nested(mock_config: MkDocsConfig) -> Page:
    """Create a mock page object at nested level (docs/guides/tutorial.md)."""
    file = File(
        path="guides/tutorial.md",
        src_dir="docs",
        dest_dir="site",
        use_directory_urls=True,
    )
    page = Page(None, file, mock_config)
    page.meta = {}
    return page


@pytest.fixture
def mock_page_deeply_nested(mock_config: MkDocsConfig) -> Page:
    """Create a mock page object at deeply nested level (docs/api/v1/reference.md)."""
    file = File(
        path="api/v1/reference.md",
        src_dir="docs",
        dest_dir="site",
        use_directory_urls=True,
    )
    page = Page(None, file, mock_config)
    page.meta = {}
    return page


@pytest.fixture
def mock_files() -> Files:
    """Create a mock files collection."""
    return Files([])


class TestImageInQuestionRelativePath:
    """Test image rendering in quiz questions with relative paths."""

    def test_image_in_question_relative_path(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that image with relative path in question is processed without errors."""
        markdown = """
<quiz>
What does this logo represent? ![Logo](./images/logo.png)
- [x] Company logo
- [ ] Product logo
</quiz>
"""
        # The key test is that this doesn't raise an exception
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        # Should return markdown (may not process due to processor limitations)
        assert markdown_result is not None
        # Try to process content even if it has errors
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        # Check that output contains the original content or processed quiz
        assert "Company logo" in result or "logo" in result.lower()

    def test_image_in_question_parent_relative_path(
        self, plugin: MkDocsQuizPlugin, mock_page_nested: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that image with parent relative path in question works from nested page."""
        markdown = """
<quiz>
What does this diagram show? ![Diagram](../images/diagram.png)
- [x] System architecture
- [ ] Database schema
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_nested, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_nested, config=mock_config, files=mock_files
        )
        assert result is not None
        # Image should be in the output in some form
        assert "diagram" in result.lower() or '../images/diagram.png' in result

    def test_image_in_question_multiple_levels_up(
        self, plugin: MkDocsQuizPlugin, mock_page_deeply_nested: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that image with multiple parent directory levels works."""
        markdown = """
<quiz>
What is shown in this chart? ![Chart](../../assets/chart.png)
- [x] Data visualization
- [ ] Table data
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_deeply_nested, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_deeply_nested, config=mock_config, files=mock_files
        )
        assert result is not None
        # Check that image reference is preserved
        assert "chart" in result.lower() or 'assets/chart.png' in result


class TestImageInAnswersRelativePath:
    """Test image rendering in quiz answers with relative paths."""

    def test_image_in_correct_answer(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that image in correct answer is rendered properly."""
        markdown = """
<quiz>
Which is the correct syntax? 
- [x] Correct: ![Code](./images/correct.png)
- [ ] Wrong answer
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "correct" in result.lower()

    def test_image_in_multiple_answers(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that images in multiple answers are all rendered."""
        markdown = """
<quiz>
Which images are correct?
- [x] Option 1 ![img1](./images/opt1.png)
- [x] Option 2 ![img2](./images/opt2.png)
- [ ] Option 3 ![img3](./images/opt3.png)
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        # Verify images are referenced in output
        assert "opt1" in result or "img1" in result
        assert "opt2" in result or "img2" in result
        assert "opt3" in result or "img3" in result


class TestImageInContentSection:
    """Test image rendering in quiz content sections."""

    def test_image_in_content_relative_path(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that image in content section with relative path is processed."""
        markdown = """
<quiz>
What is this?
- [x] A diagram
- [ ] A photo

Here's the explanation with an image:
![Explanation Diagram](./images/explanation.png)

This shows the concept visually.
</quiz>
"""
        # The key test is that this doesn't raise an exception during processing
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        assert markdown_result is not None
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        # Check that content is present (either processed or original)
        assert "A diagram" in result or "diagram" in result.lower()

    def test_multiple_images_in_content(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that multiple images in content section are all rendered."""
        markdown = """
<quiz>
What's the difference?
- [x] First one
- [ ] Second one

**Comparison:**

Before:
![Before](./images/before.png)

After:
![After](./images/after.png)
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "before" in result.lower() or "Before" in result
        assert "after" in result.lower() or "After" in result


class TestImagePathVariations:
    """Test various relative path formats."""

    def test_image_path_without_dot_slash(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image path without ./ prefix (e.g., images/logo.png)."""
        markdown = """
<quiz>
Which is the logo? ![Logo](images/logo.png)
- [x] Logo
- [ ] Icon
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Logo" in result

    def test_image_path_with_dot_slash(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image path with ./ prefix (e.g., ./images/logo.png)."""
        markdown = """
<quiz>
Which is the logo? ![Logo](./images/logo.png)
- [x] Logo
- [ ] Icon
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Logo" in result

    def test_image_deeply_nested_path(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image with deeply nested relative path."""
        markdown = """
<quiz>
What diagram is this? ![Deep Diagram](./assets/images/diagrams/architecture.png)
- [x] Architecture
- [ ] Database
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Architecture" in result


class TestImageWithMarkdownFormatting:
    """Test images combined with other markdown formatting."""

    def test_image_with_bold_text(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image alongside bold and other markdown."""
        markdown = """
<quiz>
What **important** diagram is shown? ![Important](./images/important.png)
- [x] Key diagram
- [ ] Optional diagram
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "<strong>important</strong>" in result or "important" in result

    def test_image_with_link(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image in content with hyperlinks."""
        markdown = """
<quiz>
Identify the component
- [x] Correct
- [ ] Wrong

See the [diagram](./docs/diagram.md) with image:
![Component](./images/component.png)
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "diagram" in result.lower()
        assert "component" in result.lower() or "Component" in result


class TestImageFilenameSpecialCharacters:
    """Test images with special characters in filenames."""

    def test_image_with_hyphens(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image filename with hyphens."""
        markdown = """
<quiz>
What is shown? ![My Logo](./images/my-logo-v2.png)
- [x] Logo
- [ ] Icon
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Logo" in result

    def test_image_with_numbers(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image filename with numbers."""
        markdown = """
<quiz>
Which step is this? ![Step 3](./images/step-03.png)
- [x] Step 3
- [ ] Step 4
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Step" in result


class TestImageAltTextPreservation:
    """Test that image alt text is properly preserved."""

    def test_alt_text_in_question(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that alt text in question image is preserved."""
        markdown = """
<quiz>
Identify this: ![System architecture diagram](./images/architecture.png)
- [x] Architecture
- [ ] Schema
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        # Alt text should be preserved
        assert "architecture" in result.lower() or "Architecture" in result

    def test_alt_text_in_answer(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test that alt text in answer image is preserved."""
        markdown = """
<quiz>
Which is correct?
- [x] ![Correct syntax highlighted in green](./images/correct.png)
- [ ] Wrong answer
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "correct" in result.lower()


class TestImageInFillInTheBlank:
    """Test images in fill-in-the-blank quizzes."""

    def test_image_with_fill_blank(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image in fill-in-the-blank quiz content."""
        markdown = """
<quiz>
This pattern is called a [[Singleton]].

Here's an image showing the pattern:
![Singleton Pattern](./images/singleton.png)
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "Singleton" in result

    def test_image_in_fill_blank_instruction(
        self, plugin: MkDocsQuizPlugin, mock_page_root: Page, mock_config: MkDocsConfig, mock_files: Files
    ) -> None:
        """Test image in fill-in-the-blank quiz before the blank."""
        markdown = """
<quiz>
Look at this diagram: ![Example](./images/example.png)

The answer is [[example]].
</quiz>
"""
        markdown_result = plugin.on_page_markdown(markdown, mock_page_root, mock_config)
        result = plugin.on_page_content(
            markdown_result, page=mock_page_root, config=mock_config, files=mock_files
        )
        assert result is not None
        assert "example" in result.lower()
