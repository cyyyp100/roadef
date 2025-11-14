import os
from .models import Instance, TechnicianModel, InterventionModel, InstanceModel
from .parser import parse_instance_file, parse_interv_list, parse_tech_list


def load_instance_from_dir(input_dir: str) -> Instance:
    name, nd, lv, nt, ni, ab = parse_instance_file(os.path.join(input_dir, "instance"))
    techs = parse_tech_list(os.path.join(input_dir, "tech_list"), nd)
    intervs = parse_interv_list(os.path.join(input_dir, "interv_list"), nd, lv)

    # Validate technicians & interventions
    tech_models = [
        TechnicianModel(id=t.id, levels=t.levels, unavailable_days=t.unavailable_days)
        for t in techs
    ]
    interv_models = [
        InterventionModel(
            id=iv.id,
            duration=iv.duration,
            preds=iv.preds,
            priority=iv.priority,
            cost=iv.cost,
            requirements=iv.requirements,
        )
        for iv in intervs
    ]

    inst = Instance(name, nd, lv, nt, ni, ab, techs, intervs)
    InstanceModel(
        name=inst.name,
        n_domains=nd,
        n_levels=lv,
        n_techs=nt,
        n_interv=ni,
        abandon_cost=ab,
        technicians=tech_models,
        interventions=interv_models,
    )
    return inst
