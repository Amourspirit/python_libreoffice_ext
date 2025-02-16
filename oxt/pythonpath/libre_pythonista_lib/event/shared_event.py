from __future__ import annotations
from typing import TYPE_CHECKING

# from ooodev.loader import Lo
# from ooodev.events.lo_events import LoEvents
# from ooodev.events.args.event_args import EventArgs
# from ooodev.events.lo_events import LoEvents
# from ooodev.events.args.event_args import EventArgs
# from ooodev.utils.helper.dot_dict import DotDict

# from ..const.event_const import GBL_DOC_CLOSING
# from ..ex.exceptions import SingletonKeyError

if TYPE_CHECKING:
    from oxt.pythonpath.libre_pythonista_lib.event.doc_event_partial import DocEventPartial
    from oxt.pythonpath.libre_pythonista_lib.doc.doc_globals import DocGlobals
    from ooodev.proto.office_document_t import OfficeDocumentT

else:
    from libre_pythonista_lib.doc.doc_globals import DocGlobals
    from libre_pythonista_lib.event.doc_event_partial import DocEventPartial

_SHARED_EVENT_KEY = "libre_pythonista_lib.event.shared_event.SharedEvent"


class SharedEvent(DocEventPartial):
    def __new__(cls, doc: OfficeDocumentT | None = None) -> SharedEvent:
        gbl_cache = DocGlobals.get_current()
        if _SHARED_EVENT_KEY in gbl_cache.mem_cache:
            return gbl_cache.mem_cache[_SHARED_EVENT_KEY]

        inst = super(SharedEvent, cls).__new__(cls)
        inst._is_init = False
        inst.__init__(doc)
        gbl_cache.mem_cache[_SHARED_EVENT_KEY] = inst
        return inst

        # if doc is None:
        #     eargs = EventArgs(cls)
        #     eargs.event_data = DotDict(class_name=cls.__name__, doc=None)
        #     LoEvents().trigger("LibrePythonistaSharedEventGetDoc", eargs)
        #     if eargs.event_data.doc is not None:
        #         doc = eargs.event_data.doc
        #     if doc is None:
        #         try:
        #             doc = Lo.current_doc
        #         except Exception as e:
        #             raise SingletonKeyError(
        #                 f"Error getting single key for class name: {cls.__name__}"
        #             ) from e

        # key = f"doc_{doc.runtime_uid}"
        # if key not in cls._instances:
        #     inst = super(SharedEvent, cls).__new__(cls)
        #     inst._is_init = False
        #     inst.__init__(doc)
        #     cls._instances[key] = inst

        # return cls._instances[key]

    def __init__(self, doc: OfficeDocumentT | None = None) -> None:
        if getattr(self, "_is_init", True):
            return
        DocEventPartial.__init__(self, doc=doc)
        # self._doc = doc
        self._is_init = True
