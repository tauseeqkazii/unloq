from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from decimal import Decimal


# ---------------------------------------------------------------------------
# OakfieldDevelopment
# ---------------------------------------------------------------------------

class OakfieldDevelopmentBase(BaseModel):
    dev_code: str
    development_name: Optional[str] = None
    region: Optional[str] = None
    site_manager: Optional[str] = None
    character: Optional[str] = None
    target_basket_min: Optional[float] = None
    target_basket_max: Optional[float] = None
    plot_count_min: Optional[int] = None
    plot_count_max: Optional[int] = None
    notes: Optional[str] = None


class OakfieldDevelopmentCreate(OakfieldDevelopmentBase):
    pass


class OakfieldDevelopmentUpdate(BaseModel):
    development_name: Optional[str] = None
    region: Optional[str] = None
    site_manager: Optional[str] = None
    character: Optional[str] = None
    target_basket_min: Optional[float] = None
    target_basket_max: Optional[float] = None
    plot_count_min: Optional[int] = None
    plot_count_max: Optional[int] = None
    notes: Optional[str] = None


class OakfieldDevelopmentResponse(OakfieldDevelopmentBase):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# OakfieldHouseType
# ---------------------------------------------------------------------------

class OakfieldHouseTypeBase(BaseModel):
    name: Optional[str] = None
    beds: Optional[int] = None
    base_price: Optional[float] = None
    margin_target_percent: Optional[float] = None
    typical_spend_min: Optional[float] = None
    typical_spend_max: Optional[float] = None
    available_at: Optional[str] = None


class OakfieldHouseTypeCreate(OakfieldHouseTypeBase):
    pass


class OakfieldHouseTypeUpdate(OakfieldHouseTypeBase):
    pass


class OakfieldHouseTypeResponse(OakfieldHouseTypeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# OakfieldOption
# ---------------------------------------------------------------------------

class OakfieldOptionBase(BaseModel):
    option_code: str
    display_name: Optional[str] = None
    category: Optional[str] = None
    internal_cost: Optional[float] = None
    selling_price: Optional[float] = None
    margin_percent: Optional[float] = None
    notes: Optional[str] = None


class OakfieldOptionCreate(OakfieldOptionBase):
    pass


class OakfieldOptionUpdate(BaseModel):
    display_name: Optional[str] = None
    category: Optional[str] = None
    internal_cost: Optional[float] = None
    selling_price: Optional[float] = None
    margin_percent: Optional[float] = None
    notes: Optional[str] = None


class OakfieldOptionResponse(OakfieldOptionBase):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# OakfieldBundle
# ---------------------------------------------------------------------------

class OakfieldBundleBase(BaseModel):
    bundle_code: str
    bundle_name: Optional[str] = None
    description: Optional[str] = None
    additional_revenue: Optional[float] = None
    additional_margin: Optional[float] = None
    margin_percent: Optional[float] = None


class OakfieldBundleCreate(OakfieldBundleBase):
    pass


class OakfieldBundleUpdate(BaseModel):
    bundle_name: Optional[str] = None
    description: Optional[str] = None
    additional_revenue: Optional[float] = None
    additional_margin: Optional[float] = None
    margin_percent: Optional[float] = None


class OakfieldBundleResponse(OakfieldBundleBase):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# OakfieldBundleRule
# ---------------------------------------------------------------------------

class OakfieldBundleRuleBase(BaseModel):
    bundle_code: str
    rule_type: Optional[str] = None
    condition: Optional[str] = None
    required_options: Optional[Any] = None
    excluded_options: Optional[Any] = None
    min_beds: Optional[int] = None
    allowed_build_stages: Optional[Any] = None
    min_options_revenue: Optional[float] = None
    effect_revenue: Optional[float] = None
    effect_margin: Optional[float] = None


class OakfieldBundleRuleCreate(OakfieldBundleRuleBase):
    pass


class OakfieldBundleRuleUpdate(BaseModel):
    rule_type: Optional[str] = None
    condition: Optional[str] = None
    required_options: Optional[Any] = None
    excluded_options: Optional[Any] = None
    min_beds: Optional[int] = None
    allowed_build_stages: Optional[Any] = None
    min_options_revenue: Optional[float] = None
    effect_revenue: Optional[float] = None
    effect_margin: Optional[float] = None


class OakfieldBundleRuleResponse(OakfieldBundleRuleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# OakfieldOptionBasket
# ---------------------------------------------------------------------------

class OakfieldOptionBasketBase(BaseModel):
    development_code: Optional[str] = None
    character: Optional[str] = None
    plot_reference: Optional[str] = None
    house_type: Optional[str] = None
    beds: Optional[int] = None
    customer_name: Optional[str] = None
    build_stage: Optional[str] = None
    selected_options: Optional[Any] = None
    options_revenue: Optional[float] = None
    options_cost: Optional[float] = None
    options_margin_percent: Optional[float] = None
    margin_target_percent: Optional[float] = None
    margin_delta_percent: Optional[float] = None
    bundles_triggered: Optional[Any] = None
    bundle_offered: Optional[str] = None
    demo_purpose: Optional[str] = None


class OakfieldOptionBasketCreate(OakfieldOptionBasketBase):
    pass


class OakfieldOptionBasketUpdate(BaseModel):
    selected_options: Optional[Any] = None
    options_revenue: Optional[float] = None
    options_cost: Optional[float] = None
    options_margin_percent: Optional[float] = None
    margin_target_percent: Optional[float] = None
    margin_delta_percent: Optional[float] = None
    bundles_triggered: Optional[Any] = None
    bundle_offered: Optional[str] = None
    build_stage: Optional[str] = None
    demo_purpose: Optional[str] = None


class OakfieldOptionBasketResponse(OakfieldOptionBasketBase):
    id: int
    model_config = ConfigDict(from_attributes=True)