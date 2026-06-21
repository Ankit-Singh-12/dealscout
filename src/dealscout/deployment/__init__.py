"""Modal serverless deployment of the fine-tuned pricing model.

These modules are deployed to Model with `modal deploy`, e.g:

    uv run modal deploy -m dealscout.deployment.dealscout_service2
    
They intentionally avoid importing the rest of the dealscout package, because
they run inside Modal's remote containers with their own image definition.

"""