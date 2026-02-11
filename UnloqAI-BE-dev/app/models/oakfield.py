import uuid # from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON, Boolean # from sqlalchemy.orm import relationship # from sqlalchemy.dialects.postgresql import UUID # from sqlalchemy.sql import func # from app.models.base import Base from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON from sqlalchemy.orm import relationship from app.models.base import Base class OakfieldDevelopment(Base): __tablename__ = "oakfield_developments" dev_code = Column(String, primary_key=True) development_name = Column(String) region = Column(String) site_manager = Column(String) character = Column(String) target_basket_min = Column(Float) target_basket_max = Column(Float) plot_count_min = Column(Integer) plot_count_max = Column(Integer) notes = Column(String) class OakfieldHouseType(Base): __tablename__ = "oakfield_house_types" id = Column(Integer, primary_key=True) name = Column(String) beds = Column(Integer) base_price = Column(Float) margin_target_percent = Column(Float) typical_spend_min = Column(Float) typical_spend_max = Column(Float) available_at = Column(String) class OakfieldOption(Base): __tablename__ = "oakfield_options" option_code = Column(String, primary_key=True) display_name = Column(String) category = Column(String) internal_cost = Column(Float) selling_price = Column(Float) margin_percent = Column(Float) notes = Column(String) class OakfieldBundle(Base): __tablename__ = "oakfield_bundles" bundle_code = Column(String, primary_key=True) bundle_name = Column(String) description = Column(String) additional_revenue = Column(Float) additional_margin = Column(Float) margin_percent = Column(Float) class OakfieldBundleRule(Base): __tablename__ = "oakfield_bundle_rules" id = Column(Integer, primary_key=True) bundle_code = Column(String, ForeignKey("oakfield_bundles.bundle_code")) rule_type = Column(String) condition = Column(String) required_options = Column(JSON) excluded_options = Column(JSON) min_beds = Column(Integer) allowed_build_stages = Column(JSON) min_options_revenue = Column(Float) effect_revenue = Column(Float) effect_margin = Column(Float) class OakfieldOptionBasket(Base): __tablename__ = "oakfield_option_baskets" id = Column(Integer, primary_key=True) development_code = Column(String, ForeignKey("oakfield_developments.dev_code")) character = Column(String) plot_reference = Column(String) house_type = Column(String) beds = Column(Integer) customer_name = Column(String) build_stage = Column(String) selected_options = Column(JSON) options_revenue = Column(Float) options_cost = Column(Float) options_margin_percent = Column(Float) margin_target_percent = Column(Float) margin_delta_percent = Column(Float) bundles_triggered = Column(JSON) bundle_offered = Column(String) demo_purpose = Column(String)import uuid # from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON, Boolean # from sqlalchemy.orm import relationship # from sqlalchemy.dialects.postgresql import UUID # from sqlalchemy.sql import func # from app.models.base import Base from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON from sqlalchemy.orm import relationship from app.models.base import Base class OakfieldDevelopment(Base): __tablename__ = "oakfield_developments" dev_code = Column(String, primary_key=True) development_name = Column(String) region = Column(String) site_manager = Column(String) character = Column(String) target_basket_min = Column(Float) target_basket_max = Column(Float) plot_count_min = Column(Integer) plot_count_max = Column(Integer) notes = Column(String) class OakfieldHouseType(Base): __tablename__ = "oakfield_house_types" id = Column(Integer, primary_key=True) name = Column(String) beds = Column(Integer) base_price = Column(Float) margin_target_percent = Column(Float) typical_spend_min = Column(Float) typical_spend_max = Column(Float) available_at = Column(String) class OakfieldOption(Base): __tablename__ = "oakfield_options" option_code = Column(String, primary_key=True) display_name = Column(String) category = Column(String) internal_cost = Column(Float) selling_price = Column(Float) margin_percent = Column(Float) notes = Column(String) class OakfieldBundle(Base): __tablename__ = "oakfield_bundles" bundle_code = Column(String, primary_key=True) bundle_name = Column(String) description = Column(String) additional_revenue = Column(Float) additional_margin = Column(Float) margin_percent = Column(Float) class OakfieldBundleRule(Base): __tablename__ = "oakfield_bundle_rules" id = Column(Integer, primary_key=True) bundle_code = Column(String, ForeignKey("oakfield_bundles.bundle_code")) rule_type = Column(String) condition = Column(String) required_options = Column(JSON) excluded_options = Column(JSON) min_beds = Column(Integer) allowed_build_stages = Column(JSON) min_options_revenue = Column(Float) effect_revenue = Column(Float) effect_margin = Column(Float) class OakfieldOptionBasket(Base): __tablename__ = "oakfield_option_baskets" id = Column(Integer, primary_key=True) development_code = Column(String, ForeignKey("oakfield_developments.dev_code")) character = Column(String) plot_reference = Column(String) house_type = Column(String) beds = Column(Integer) customer_name = Column(String) build_stage = Column(String) selected_options = Column(JSON) options_revenue = Column(Float) options_cost = Column(Float) options_margin_percent = Column(Float) margin_target_percent = Column(Float) margin_delta_percent = Column(Float) bundles_triggered = Column(JSON) bundle_offered = Column(String) demo_purpose = Column(String)import uuid # from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON, Boolean # from sqlalchemy.orm import relationship # from sqlalchemy.dialects.postgresql import UUID # from sqlalchemy.sql import func # from app.models.base import Base from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON from sqlalchemy.orm import relationship from app.models.base import Base class OakfieldDevelopment(Base): __tablename__ = "oakfield_developments" dev_code = Column(String, primary_key=True) development_name = Column(String) region = Column(String) site_manager = Column(String) character = Column(String) target_basket_min = Column(Float) target_basket_max = Column(Float) plot_count_min = Column(Integer) plot_count_max = Column(Integer) notes = Column(String) class OakfieldHouseType(Base): __tablename__ = "oakfield_house_types" id = Column(Integer, primary_key=True) name = Column(String) beds = Column(Integer) base_price = Column(Float) margin_target_percent = Column(Float) typical_spend_min = Column(Float) typical_spend_max = Column(Float) available_at = Column(String) class OakfieldOption(Base): __tablename__ = "oakfield_options" option_code = Column(String, primary_key=True) display_name = Column(String) category = Column(String) internal_cost = Column(Float) selling_price = Column(Float) margin_percent = Column(Float) notes = Column(String) class OakfieldBundle(Base): __tablename__ = "oakfield_bundles" bundle_code = Column(String, primary_key=True) bundle_name = Column(String) description = Column(String) additional_revenue = Column(Float) additional_margin = Column(Float) margin_percent = Column(Float) class OakfieldBundleRule(Base): __tablename__ = "oakfield_bundle_rules" id = Column(Integer, primary_key=True) bundle_code = Column(String, ForeignKey("oakfield_bundles.bundle_code")) rule_type = Column(String) condition = Column(String) required_options = Column(JSON) excluded_options = Column(JSON) min_beds = Column(Integer) allowed_build_stages = Column(JSON) min_options_revenue = Column(Float) effect_revenue = Column(Float) effect_margin = Column(Float) class OakfieldOptionBasket(Base): __tablename__ = "oakfield_option_baskets" id = Column(Integer, primary_key=True) development_code = Column(String, ForeignKey("oakfield_developments.dev_code")) character = Column(String) plot_reference = Column(String) house_type = Column(String) beds = Column(Integer) customer_name = Column(String) build_stage = Column(String) selected_options = Column(JSON) options_revenue = Column(Float) options_cost = Column(Float) options_margin_percent = Column(Float) margin_target_percent = Column(Float) margin_delta_percent = Column(Float) bundles_triggered = Column(JSON) bundle_offered = Column(String) demo_purpose = Column(String)import uuid
# from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON, Boolean
# from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.sql import func
# from app.models.base import Base

from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base


class OakfieldDevelopment(Base):
    __tablename__ = "oakfield_developments"

    dev_code = Column(String, primary_key=True)
    development_name = Column(String)
    region = Column(String)
    site_manager = Column(String)
    character = Column(String)

    target_basket_min = Column(Float)
    target_basket_max = Column(Float)

    plot_count_min = Column(Integer)
    plot_count_max = Column(Integer)

    notes = Column(String)


class OakfieldHouseType(Base):
    __tablename__ = "oakfield_house_types"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    beds = Column(Integer)
    base_price = Column(Float)
    margin_target_percent = Column(Float)

    typical_spend_min = Column(Float)
    typical_spend_max = Column(Float)

    available_at = Column(String)


class OakfieldOption(Base):
    __tablename__ = "oakfield_options"

    option_code = Column(String, primary_key=True)
    display_name = Column(String)
    category = Column(String)
    internal_cost = Column(Float)
    selling_price = Column(Float)
    margin_percent = Column(Float)
    notes = Column(String)


class OakfieldBundle(Base):
    __tablename__ = "oakfield_bundles"

    bundle_code = Column(String, primary_key=True)
    bundle_name = Column(String)
    description = Column(String)
    additional_revenue = Column(Float)
    additional_margin = Column(Float)
    margin_percent = Column(Float)


class OakfieldBundleRule(Base):
    __tablename__ = "oakfield_bundle_rules"

    id = Column(Integer, primary_key=True)
    bundle_code = Column(String, ForeignKey("oakfield_bundles.bundle_code"))

    rule_type = Column(String)
    condition = Column(String)

    required_options = Column(JSON)
    excluded_options = Column(JSON)

    min_beds = Column(Integer)
    allowed_build_stages = Column(JSON)

    min_options_revenue = Column(Float)

    effect_revenue = Column(Float)
    effect_margin = Column(Float)


class OakfieldOptionBasket(Base):
    __tablename__ = "oakfield_option_baskets"

    id = Column(Integer, primary_key=True)

    development_code = Column(String, ForeignKey("oakfield_developments.dev_code"))
    character = Column(String)

    plot_reference = Column(String)
    house_type = Column(String)
    beds = Column(Integer)

    customer_name = Column(String)
    build_stage = Column(String)

    selected_options = Column(JSON)

    options_revenue = Column(Float)
    options_cost = Column(Float)

    options_margin_percent = Column(Float)
    margin_target_percent = Column(Float)
    margin_delta_percent = Column(Float)

    bundles_triggered = Column(JSON)
    bundle_offered = Column(String)

    demo_purpose = Column(String)

