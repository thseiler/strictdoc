from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import BaseCase
from typing_extensions import deprecated

from tests.end2end.helpers.components.collapsible_list import CollapsibleList
from tests.end2end.helpers.components.node.document_root import DocumentRoot
from tests.end2end.helpers.components.node.requirement import Requirement
from tests.end2end.helpers.components.node.section import Section
from tests.end2end.helpers.components.toc import TOC


class Screen:  # pylint: disable=invalid-name, too-many-public-methods
    def __init__(self, test_case: BaseCase) -> None:
        assert isinstance(test_case, BaseCase)
        self.test_case: BaseCase = test_case

    def assert_no_js_and_404_errors(self) -> None:
        self.test_case.assert_no_404_errors()
        self.test_case.assert_no_js_errors()

    def assert_text(self, text: str) -> None:
        self.test_case.assert_text(text)

    def assert_no_text(self, text: str) -> None:
        self.test_case.assert_element_not_present(
            f"//*[contains(., '{text}')]", by=By.XPATH
        )

    # Assert fields content:
    # Method with the 'field_name' can be used,
    # but named methods are recommended.

    def assert_xpath_contains(self, xpath: str, text: str) -> None:
        # screen shared
        self.test_case.assert_element(
            f"{xpath}[contains(., '{text}')]", by=By.XPATH
        )

    # body

    def assert_on_screen(self, viewtype: str):
        self.test_case.assert_element(
            f'//body[@data-viewtype="{viewtype}"]',
            by=By.XPATH,
        )
        self.test_case.wait_for_ready_state_complete()

    # Header.
    # Document title (all views)

    def assert_header_document_title(self, document_title: str) -> None:
        self.test_case.assert_element(
            "//*[@class='header__document_title']"
            f"[contains(., '{document_title}')]",
            by=By.XPATH,
        )

    # Empty pages.
    # Valid only for 3 views:
    # table & traceability & deep-traceability,
    # overridden for the document view.

    def assert_empty_view(
        self, placeholder: str = "document-main-placeholder"
    ) -> None:
        self.test_case.assert_element(f'//*[@data-testid="{placeholder}"]')

    def assert_not_empty_view(
        self, placeholder: str = "document-main-placeholder"
    ) -> None:
        self.test_case.assert_element_not_visible(
            f'//*[@data-testid="{placeholder}"]'
        )

    # Get:

    # DocumentRoot
    def get_root_node(self) -> DocumentRoot:
        DocumentRoot(self.test_case).assert_is_root_node()
        return DocumentRoot(self.test_case)

    # Section
    def get_section(self, node_order: int = 1) -> Section:
        Section(self.test_case, node_order).assert_is_section()
        return Section(self.test_case, node_order)

    @deprecated("Use get_node instead.")
    def get_requirement(self, node_order: int = 1) -> Requirement:
        return self.get_node(node_order)

    def get_node(self, node_order: int = 1) -> Requirement:
        """
        Based on "//sdoc-node[@data-testid='node-requirement']"
        """
        requirement = Requirement.with_node(self.test_case, node_order)
        requirement.assert_is_requirement()
        return requirement

    def get_requirement_modal(self, node_order: int = -1) -> Requirement:
        """
        Based on "//sdoc-node-content". Searches for an <sdoc-node-content>
        without taking the node <sdoc-node> into account.

        Args:
            node_order (int, optional): The requirement in the modal window
            will always be the last one on the page.
            Defaults to -1. But this option does not work.
            Must specify the parameter explicitly.

        Returns:
            Requirement: Asserts for all fields are available.
        """
        requirement = Requirement.without_node(self.test_case, node_order)
        requirement.assert_is_requirement()
        return requirement

    #
    # TOC
    #
    def get_toc(self) -> TOC:
        TOC(self.test_case).assert_is_toc()
        return TOC(self.test_case)

    def assert_toc_contains(self, string: str) -> None:
        TOC(self.test_case).assert_toc_contains(string)

    def assert_toc_contains_not(self, string: str) -> None:
        TOC(self.test_case).assert_toc_contains_not(string)

    #
    # CollapsibleList
    #
    def get_collapsible_list(self) -> CollapsibleList:
        CollapsibleList(self.test_case).assert_is_collapsible()
        return CollapsibleList(self.test_case)

    def do_fill_in_field_value(
        self, field_xpath: str, field_value: str
    ) -> None:
        self.test_case.type(field_xpath, f"{field_value}", by=By.XPATH)

        WebDriverWait(self.test_case.driver, timeout=3).until(
            lambda _: self.test_case.get_value(field_xpath, by=By.XPATH)
            == field_value
        )
